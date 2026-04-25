from pydantic import BaseModel, EmailStr, constr, Field



class UserCreate(BaseModel):

    username: str
    firstname: str 
    lastname: str
    email: EmailStr
    password: constr(min_length=8, max_length=72)



class UserLogin(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=72)




