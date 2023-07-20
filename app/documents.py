from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import BabyName, FamousPerson

@registry.register_document
class BabyNameDocument(Document):
    class Index:
        name = 'babynames'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = BabyName
        fields = [
            'name',
            'gender',
            'description',
            'boy_rank',
            'girl_rank',
            'name_variants',
            'ethnicity',
            'religion',
            'language',
            'region',
        ]

@registry.register_document
class FamousPersonDocument(Document):
    class Index:
        name = 'famouspeople'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = FamousPerson
        fields = [
            'name',
            'first_name',
            'description',
            'wikipedia_link',
        ]