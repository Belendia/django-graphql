from django.utils import timezone
from graphene_django import DjangoObjectType
import graphene

from apps.users.models import User as UserModel
from apps.decks.models import Deck as DeckModel
from apps.cards.models import Card as CardModel

buckets = (
    (1, 1),
    (2, 3),
    (3, 7),
    (4, 16),
    (5, 30),
)


def return_date_time(days):
    now = timezone.now()
    return now + timezone.timedelta(days=days)


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


class UpdateCard(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        id = graphene.ID()
        question = graphene.String(required=True)
        answer = graphene.String()
        # easy, average, or difficult -> 1, 2, 3
        status = graphene.Int()

    # The class attributes define the response of the mutation
    card = graphene.Field(Card)

    def mutate(self, info, id, question, answer, status):
        c = CardModel.objects.get(id=id)

        bucket = c.bucket
        if status == 1 and bucket > 1:
            bucket -= 1
        elif status == 3 and bucket <= 4:
            bucket += 1

        # Calculate next review at date
        days = buckets[bucket - 1][1]
        next_review_at = return_date_time(days)

        c.question = question
        c.answer = answer
        c.bucket = bucket
        c.next_review_at = next_review_at
        c.last_reviewed_at = timezone.now()

        c.save()
        # Notice we return an instance of this mutation
        return UpdateCard(card=c)


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
    update_card = UpdateCard.Field()


class Query(graphene.ObjectType):
    users = graphene.List(User)
    decks = graphene.List(Deck)
    deck_by_id = graphene.Field(Deck, id=graphene.Int())
    cards = graphene.List(Card)
    deck_cards = graphene.List(Card, deck=graphene.Int())

    def resolve_users(self, info):
        return UserModel.objects.all()

    def resolve_decks(self, info):
        return DeckModel.objects.all()

    def resolve_deck_by_id(self, info, id):
        return DeckModel.objects.get(pk=id)

    def resolve_cards(self, info):
        return CardModel.objects.all()

    def resolve_deck_cards(self, info, deck):
        return CardModel.objects.filter(deck=deck)


schema = graphene.Schema(query=Query, mutation=Mutation)
