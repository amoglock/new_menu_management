import uuid

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    id: uuid.UUID = Field(default=uuid.uuid4())
    title: str
    description: str

    # class Config:
    #     from_attributes = True


class MenuResponse(BaseResponse):
    submenus_count: int = 0
    dishes_count: int = 0


class CreateMenu(BaseModel):
    title: str
    description: str

    def to_dict(self):
        return self.model_dump(exclude={'id'})


class PatchMenu(CreateMenu):
    pass


class SubmenuResponse(BaseResponse):
    dishes_count: int = 0


class CreateSubmenu(CreateMenu):
    pass


class PatchSubmenu(CreateSubmenu):
    pass


class DishResponse(BaseResponse):
    title: str
    description: str
    price: str


class CreateDish(BaseModel):
    title: str
    description: str
    price: str

    def to_dict(self):
        return self.model_dump(exclude={'id'})


class PatchDish(CreateSubmenu):
    price: str
