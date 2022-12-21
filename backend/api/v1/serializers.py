from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Recipe, Tag, IngredientRecipe,
                            Ingredient, FavoriteRecipe, ShoppingList)
from users.models import User, Follow
from drf_base64.fields import Base64ImageField


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return not user.is_anonymous and Follow.objects.filter(
            user=user,
            author=author.id
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientAmountRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        queryset = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientAmountRecipeSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(recipe=obj,
                                             user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(recipe=obj,
                                           user=request.user).exists()


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags',
                  'image', 'name', 'text', 'cooking_time')

    def validate(self, attrs):
        ingredients = attrs.get('ingredients')
        print(attrs)
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты должны быть уникальными'
                })
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'ingredients': 'Количество ингредиентов должно быть больше нуля!'
                })

        tags = attrs.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Нужно выбрать хотя бы один тэг!'
            })

        cooking_time = attrs.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть больше 0!'
            })
        return attrs

    @staticmethod
    def add_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            IngredientRecipe.objects.update_or_create(
                recipe=recipe, ingredient=ingredient['id'], amount=ingredient['amount']
            )

    @staticmethod
    def update_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_ingredients(ingredients, recipe)
        self.update_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.add_ingredients(validated_data.pop('ingredients'), instance)
        self.update_tags(validated_data.pop('tags'), instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = attrs.get('recipe')
        if FavoriteRecipe.objects.filter(user=request.user, recipe=recipe).exist():
            raise serializers.ValidationError({
                'status': 'Рецепт уже есть в избранном!'
            })
        return attrs


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')


class FollowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit_recipes = request.query_params.get('recipes_limit')
        if limit_recipes is not None:
            recipes = obj.recipes.all()[:(int(limit_recipes))]
        else:
            recipes = obj.recipes.all()
        context = {'request': request}
        return FollowRecipeSerializer(recipes, many=True,
                                      context=context).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()
