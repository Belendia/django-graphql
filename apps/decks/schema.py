from graphene_django import DjangoObjectType
import graphene

from .models import Deck


class DeckType(DjangoObjectType):
    class Meta:
        model = Deck


class CreateDeckMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        title = graphene.String(required=True)
        description = graphene.String()

    # The class attributes define the response of the mutation
    deck = graphene.Field(DeckType)

    def mutate(self, info, title, description):
        d = Deck(title=title, description=description)
        d.save()
        # Notice we return an instance of this mutation
        return CreateDeckMutation(deck=d)

