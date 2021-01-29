import graphene

from apps.cards.models import Card
from apps.decks.models import Deck
from apps.users.models import User

from apps.decks.schema import (
    DeckType,
    CreateDeckMutation
)
from apps.cards.schema import (
    CardType,
    CreateCardMutation,
    UpdateCardMutation
)
from apps.users.schema import UserType


class Mutation(graphene.ObjectType):
    create_deck = CreateDeckMutation.Field()
    create_card = CreateCardMutation.Field()
    update_card = UpdateCardMutation.Field()


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    decks = graphene.List(DeckType)
    deck_by_id = graphene.Field(DeckType, id=graphene.Int())
    cards = graphene.List(CardType)
    deck_cards = graphene.List(CardType, deck=graphene.Int())

    def resolve_users(self, info):
        return User.objects.all()

    def resolve_decks(self, info):
        return Deck.objects.all()

    def resolve_deck_by_id(self, info, id):
        return Deck.objects.get(pk=id)

    def resolve_cards(self, info):
        return Card.objects.all()

    def resolve_deck_cards(self, info, deck):
        return Card.objects.filter(deck=deck)


schema = graphene.Schema(query=Query, mutation=Mutation)
