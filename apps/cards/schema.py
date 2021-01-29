import graphene
from django.utils import timezone
from graphene_django import DjangoObjectType

from .models import Card
from apps.decks.models import Deck

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


class CardType(DjangoObjectType):
    class Meta:
        model = Card


class CreateCardMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        question = graphene.String(required=True)
        answer = graphene.String()
        deck_id = graphene.Int()

    # The class attributes define the response of the mutation
    card = graphene.Field(CardType)

    def mutate(self, info, question, answer, deck_id):
        d = Deck.objects.get(pk=deck_id)
        c = Card(question=question, answer=answer, deck=d)
        c.save()
        # Notice we return an instance of this mutation
        return CreateCardMutation(card=c)


class UpdateCardMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        id = graphene.ID()
        question = graphene.String(required=True)
        answer = graphene.String()
        # easy, average, or difficult -> 1, 2, 3
        status = graphene.Int()

    # The class attributes define the response of the mutation
    card = graphene.Field(CardType)

    def mutate(self, info, id, question, answer, status):
        c = Card.objects.get(id=id)

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
        return UpdateCardMutation(card=c)
