from db import engine, Base
from models import MechanicalPDF, AluminiumPDF, SteelPDF, FoundryPDF, RadiologyPDF, RubberPDF, ChemicalPDF

Base.metadata.create_all(bind=engine)
print("✅ Tables created in public schema")
