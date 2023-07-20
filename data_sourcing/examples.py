from .models import *

famous_people_john = [
    FamousPerson(name="John Lennon", first_name="John", description="Famous musician from the band The Beatles", wikipedia_link="https://en.wikipedia.org/wiki/John_Lennon"),
    FamousPerson(name="John F. Kennedy", first_name="John", description="35th President of the United States", wikipedia_link="https://en.wikipedia.org/wiki/John_F._Kennedy")
]

famous_people_mary = [
    FamousPerson(name="Mary Shelley", first_name='Mary', description="English novelist who wrote the Gothic novel Frankenstein", wikipedia_link="https://en.wikipedia.org/wiki/Mary_Shelley"),
    FamousPerson(name="Mary, Queen of Scots", first_name="Mary", description="Queen of Scotland from 14 December 1542 to 24 July 1567", wikipedia_link="https://en.wikipedia.org/wiki/Mary,_Queen_of_Scots")
]


baby_name_john = BabyName(
    name="John",
    gender = NameGender.MALE,
    description="John is a masculine given name in the English language.",
    boy_rank=1,
    girl_rank=None,
    famous_people_list=famous_people_john,
    name_variants=["Jon", "Jhon", "Johnathan"],
    ethnicity=[Ethnicity.CAUCASIAN],
    religion=[Religion.CHRISTIANITY],
    region='Western'

)


baby_name_mary = BabyName(
    name="Mary",
    gender = NameGender.FEMALE,
    description="Mary is a traditionally feminine name with roots in Hebrew scriptures.",
    boy_rank=None,
    girl_rank=2,
    famous_people_list=famous_people_mary,
    name_variants=["Marie", "Maria"],
    ethnicity=[Ethnicity.CAUCASIAN],
    religion=[Religion.CHRISTIANITY],
    language='Hebrew',
    region='Europe'
)

baby_name_mohamed = BabyName(
    name="Mohammed",
    gender = NameGender.MALE,
    description="Arabic given male name literally meaning 'Praiseworthy' and name of the Prophet",
    boy_rank=None,
    girl_rank=2,
    famous_people_list=famous_people_mary,
    name_variants=["Muhammed", "Muhamad", "Mohammad", "Mohammed", "Mohamad", "Mohamed"],
    ethnicity=[Ethnicity.MIDDLE_EASTERN],
    religion=[Religion.ISLAM],
    language='Araibic',
    region='Middle East'
)

baby_name_jing = BabyName(
    name="Jing",
    gender = NameGender.FEMALE,
    description="Chinese given female name meaning calm",
    ethnicity=[Ethnicity.ASIAN],
    religion=[Religion.SECULAR],
    language='Chinese',
    region='China'
)

EXAMPLE_BABY_NAMES = [baby_name_jing, baby_name_john, baby_name_mary,baby_name_mohamed]
