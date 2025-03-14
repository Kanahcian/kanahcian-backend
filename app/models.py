# Purpose: Define the database schema

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, CHAR
from sqlalchemy.orm import relationship
from app.database import Base

class Account(Base):
    __tablename__ = "Account"
    
    AccountID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Name = Column(String(20), nullable=False)
    Password = Column(String(300), nullable=False)
    EntrySemester = Column(CHAR(3), nullable=False)
    Photo = Column(Text)
    
    records = relationship("Record", back_populates="account")

class Location(Base):
    __tablename__ = "Location"
    
    LocationID = Column("LocationID", Integer, primary_key=True, index=True, autoincrement=True)
    name = Column("name", String(20), index=True, nullable=False)
    Latitude = Column("Latitude", String(30), nullable=False)
    Longitude = Column("Longitude", String(30), nullable=False)
    Address = Column("Address", String(50))
    BriefDescription = Column(String(300))
    
    records = relationship("Record", back_populates="location")
    villagers = relationship("Villager", back_populates="location")

class Villager(Base):
    __tablename__ = "Villager"
    
    VillagerID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Name = Column(String(20), nullable=False)
    Gender = Column(CHAR(1), nullable=False)
    Job = Column(String(20))
    URL = Column(Text)
    Photo = Column(Text)
    Location = Column(Integer, ForeignKey("Location.LocationID"))
    
    records = relationship("VillagersAtRecord", back_populates="villager")
    location = relationship("Location", back_populates="villagers")

class Record(Base):
    __tablename__ = "Record"
    
    RecordID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Semester = Column(CHAR(3), nullable=False)
    Date = Column(Date, nullable=False)
    Photo = Column(Text)
    Description = Column(String(1000))
    Location = Column(Integer, ForeignKey("Location.LocationID"), nullable=False)
    Account = Column(Integer, ForeignKey("Account.AccountID"), nullable=False)
    
    location = relationship("Location", back_populates="records")
    account = relationship("Account", back_populates="records")
    
    students = relationship("StudentsAtRecord", back_populates="record")
    villagers = relationship("VillagersAtRecord", back_populates="record")

class StudentsAtRecord(Base):
    __tablename__ = "Students_at_record"
    
    Account = Column(Integer, ForeignKey("Account.AccountID"), primary_key=True)
    Record = Column(Integer, ForeignKey("Record.RecordID"), primary_key=True)
    
    # 關聯關係
    student = relationship("Account")
    record = relationship("Record", back_populates="students")
    
    __table_args__ = (
        # 定義複合主鍵約束
        {'schema': 'public'}
    )

class VillagersAtRecord(Base):
    __tablename__ = "Villagers_at_record"
    
    Villager = Column(Integer, ForeignKey("Villager.VillagerID"), primary_key=True)
    Record = Column(Integer, ForeignKey("Record.RecordID"), primary_key=True)
    
    # 關聯關係
    villager = relationship("Villager", back_populates="records")
    record = relationship("Record", back_populates="villagers")
    
    __table_args__ = (
        # 定義複合主鍵約束
        {'schema': 'public'}
    )


