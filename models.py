from sqlalchemy import Column, Integer, String, DateTime, func
from db import Base

class MechanicalPDF(Base):
    __tablename__ = "mechanicalpdfs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, nullable=False)
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())

class AluminiumPDF(Base):
    __tablename__ = "aluminiumpdfs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, nullable=False)
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())

class SteelPDF(Base):
    __tablename__ = "steelpdfs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, nullable=False)
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())

class FoundryPDF(Base):
    __tablename__ = "foundrypdfs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, nullable=False)
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())

class RadiologyPDF(Base):
    __tablename__ = "radiologypdfs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, nullable=False)
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())

class RubberPDF(Base):
    __tablename__ = "rubberpdfs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, nullable=False)
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())

class ChemicalPDF(Base):
    __tablename__ = "chemicalpdfs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, nullable=False)
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())
