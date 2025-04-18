# Purpose: Define the database schema

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, CHAR, ARRAY, Boolean, UniqueConstraint
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
    Photo = Column(Text)
    Tag = Column("Tag", ARRAY(String, dimensions=1))  # 使用 ARRAY 儲存多個標籤
    
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

    # 新增關聯關係
    relationships_as_source = relationship("VillagerRelationship", 
                                          foreign_keys="VillagerRelationship.SourceVillagerID",
                                          back_populates="source_villager")
    relationships_as_target = relationship("VillagerRelationship", 
                                          foreign_keys="VillagerRelationship.TargetVillagerID",
                                          back_populates="target_villager")
    
    # 輔助方法：獲取所有關係（無論是源還是目標）
    @property
    def all_relationships(self):
        return self.relationships_as_source + self.relationships_as_target

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

class RelationshipType(Base):
    __tablename__ = "RelationshipType"
    
    RelationshipTypeID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Name = Column(String(20), nullable=False, unique=True)  # 例如：父子、母子、夫妻等
    Source_Role = Column(String(20), nullable=False)  # 關係源角色，如：父親、丈夫
    Target_Role = Column(String(20), nullable=False)  # 關係目標角色，如：兒子、妻子
    Description = Column(String(100))  # 可選的關係描述
    
    # 關聯到親屬關係表
    relationships = relationship("VillagerRelationship", back_populates="relationship_type")

class VillagerRelationship(Base):
    __tablename__ = "VillagerRelationship"
    
    RelationshipID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    SourceVillagerID = Column(Integer, ForeignKey("Villager.VillagerID"), nullable=False)  # 關係源，例如父親
    TargetVillagerID = Column(Integer, ForeignKey("Villager.VillagerID"), nullable=False)  # 關係目標，例如兒子
    RelationshipTypeID = Column(Integer, ForeignKey("RelationshipType.RelationshipTypeID"), nullable=False)
    
    # 關聯關係
    source_villager = relationship("Villager", foreign_keys=[SourceVillagerID], back_populates="relationships_as_source")
    target_villager = relationship("Villager", foreign_keys=[TargetVillagerID], back_populates="relationships_as_target")
    relationship_type = relationship("RelationshipType", back_populates="relationships")
    
    # 添加唯一性約束，確保相同的兩個村民和相同的關係類型不會重複記錄
    __table_args__ = (
        UniqueConstraint('SourceVillagerID', 'TargetVillagerID', 'RelationshipTypeID', name='unique_relationship'),
    )
