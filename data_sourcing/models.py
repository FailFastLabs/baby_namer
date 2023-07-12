from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, validator
import re
import wikipediaapi


class NameGender(Enum):
    MALE = 'Male'
    FEMALE = 'Female'
    UNISEX = 'Unisex'


class Ethnicity(Enum):
    AFRICAN = 'African'
    ASIAN = 'Asian'
    CAUCASIAN = 'Caucasian'
    HISPANIC = 'Hispanic'
    MIDDLE_EASTERN = 'Middle Eastern'
    NATIVE_AMERICAN = 'Native American'
    PACIFIC_ISLANDER = 'Pacific Islander'
    TWO_OR_MORE_RACES = 'Two or More Races'
    OTHER = 'Other'
    UNKNOWN = 'Unknown'


class Religion(Enum):
    CHRISTIANITY = 'Christianity'
    ISLAM = 'Islam'
    SECULAR = 'Secular'
    HINDUISM = 'Hinduism'
    BUDDHISM = 'Buddhism'
    JUDAISM = 'Judaism'
    SIKHISM = 'Sikhism'
    BAHAI = 'Bahai'
    JAINISM = 'Jainism'
    SHINTO = 'Shinto'


class FamousPerson(BaseModel):
    name: str = Field(..., description="The name of the famous person")
    description: Optional[str] = Field(None, description="A short description of the famous person")
    wikipedia_link: HttpUrl = Field(..., description="The link to the famous person's Wikipedia page")

    @validator('wikipedia_link')
    def name_must_not_be_empty(cls, field):
        if not field:
            raise ValueError("wikipedia link must not be empty!")
        return field

    @validator('wikipedia_link')
    def link_must_work(cls, field):
        pattern = r"\/([^\/]+)$"
        wiki_wiki = wikipediaapi.Wikipedia('en')

        match = re.search(pattern, field)
        if match:
            name = match.group(1)
            page_py = wiki_wiki.page(name)
            if not page_py.exists():
                raise ValueError("wikipedia page does not exist")
        else:
            raise ValueError("wikipedia link must not be empty!")
        return field

    class Config:
        validate_assignment = True


class BabyName(BaseModel):
    name: str = Field(..., description="The baby name")
    gender: NameGender = Field(description='Names primary gender. One of [Male,Female,Unisex]', bulk=True)
    description: Optional[str] = Field(None, description="A short description of the name")
    boy_rank: Optional[int] = Field(None, description="The popularity rank of the name for boys")
    girl_rank: Optional[int] = Field(None, description="The popularity rank of the name for girls")
    # famous_people_list: Optional[List[FamousPerson]] = Field(None, description="A list of famous people who share this name")
    name_variants: Optional[List[str]] = Field(None,
                                               description="List of common spellings and related names",
                                               bulk=True)
    ethnicity: Optional[List[Ethnicity]] = Field(None,
                                                 description="The ethnicity commonly associated with this name. Acceptable values are: " + ", ".join(
                                                     [e.value for e in Ethnicity]),
                                                 bulk=True)
    religion: Optional[List[Religion]] = Field(None,
                                               description="The religion commonly associated with this name. Acceptable values are: " + ", ".join(
                                                   [r.value for r in Religion]),
                                               bulk=True)
    language: Optional[str] = Field(None, description="Language of Origin for this name",
                                    bulk=True)
    region: Optional[str] = Field(None, description="Country/State/ Location where the name is common",
                                  bulk=True)

    @validator('name')
    def name_must_not_be_empty(cls, field):
        if not field:
            raise ValueError("Name must not be empty!")
        return field

    @validator('boy_rank', 'girl_rank')
    def rank_must_be_non_negative(cls, field):
        if field is not None and field < 0:
            raise ValueError("Rank cannot be negative!")
        return field

    @validator('ethnicity')
    def ethnicity_match(cls, field):
        if field is None:
            return field
        ethnicities = [e.value for e in Ethnicity]
        for k in field:
            if k.value not in ethnicities:
                raise ValueError(f"{field.value} is not a valid ethnicity. Must be one of: {', '.join(ethnicities)}")
        return field

    @validator('religion')
    def religion_match(cls, field):
        if field is None:
            return field
        religions = [e.value for e in Religion]
        for k in field:
            if k.value not in religions:
                raise ValueError(f"{field.value} is not a valid religion. Must be one of: {', '.join(religions)}")
        return field

    class Config:
        validate_assignment = True


class BabyNameRef(BabyName):
    famous_people_list: Optional[List[FamousPerson]] = Field(None,
                                                             description="A list of famous people who share this name")
