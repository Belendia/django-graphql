from graphene_django import DjangoObjectType
import graphene
from apps.users.models import User as UserModel
from apps.decks.models import Deck as DeckModel
from apps.cards.models import Card as CardModel


class User(DjangoObjectType):
    class Meta:
        model = UserModel


class Deck(DjangoObjectType):
    class Meta:
        model = DeckModel


class Card(DjangoObjectType):
    class Meta:
        model = CardModel


class CreateCard(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        question = graphene.String(required=True)
        answer = graphene.String()
        deck_id = graphene.Int()

    # The class attributes define the response of the mutation
    card = graphene.Field(Card)

    def mutate(self, info, question, answer, deck_id):
        d = DeckModel.objects.get(pk=deck_id)
        c = CardModel(question=question, answer=answer, deck=d)
        c.save()
        # Notice we return an instance of this mutation
        return CreateCard(card=c)


class CreateDeck(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        title = graphene.String(required=True)
        description = graphene.String()

    # The class attributes define the response of the mutation
    deck = graphene.Field(Deck)

    def mutate(self, info, title, description):
        d = DeckModel(title=title, description=description)
        d.save()
        # Notice we return an instance of this mutation
        return CreateDeck(deck=d)


class Mutation(graphene.ObjectType):
    create_card = CreateCard.Field()
    create_deck = CreateDeck.Field()


class Query(graphene.ObjectType):
    users = graphene.List(User)
    decks = graphene.List(Deck)
    cards = graphene.List(Card)

    def resolve_users(self, info):
        return UserModel.objects.all()

    def resolve_decks(self, info):
        return DeckModel.objects.all()

    def resolve_cards(self, info):
        return CardModel.objects.all()


schema = graphene.Schema(query=Query, mutation=Mutation)
