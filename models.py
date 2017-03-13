from neomodel import (config, StructuredNode, StringProperty, IntegerProperty, FloatProperty, StructuredRel, RelationshipTo, RelationshipFrom)
config.DATABASE_URL = 'bolt://neo4j:password@localhost:7689'  # default

class Info(StructuredRel):
    @staticmethod
    def get_names():
        return ["Variant", "Info"]

class GenoInfo(StructuredRel):
    @staticmethod
    def get_names():
        return ["Info", "GenotypeInfo"]
    
class HasInfo(StructuredRel):
    @staticmethod
    def get_names():
        return ["GenotypeInfo", "Genotype"]

class HasVariant(StructuredRel):
    @staticmethod
    def get_names():
        return ["Chromosome", "Variant"]

class Variant(StructuredNode):
    id = StringProperty(Required=True)
    
    chrom = StringProperty()
    pos = IntegerProperty()
    ref = StringProperty()
    alt = StringProperty()
    info = RelationshipTo("VariantInfo", "Info")
    hasVariant = RelationshipFrom("Chromosome", "HasVariant")
    
    @staticmethod
    def get_names():
        return ["id", "chrom", "pos", "ref", "alt"]
        
    def get_all(self):
        return [self.id, self.chrom, self.pos, self.ref, self.alt]

class VariantInfo(StructuredNode):
    id = StringProperty(Required=True)
    
    qual = FloatProperty()
    filter = StringProperty()
    info = StringProperty()
    format = StringProperty()
    info = RelationshipFrom("Variant", "Info")
    genotypeInfo = RelationshipTo("GenotypeInfo", "GenoInfo")
    
    @staticmethod
    def get_names():
        return ["id", "qual", "filter", "info", "format"]
        
    def get_all(self):
        return [self.id, self.qual, self.filter, self.info, self.format]

class GenotypeInfo(StructuredNode):
    id = StringProperty(Required=True)
    
    info = StringProperty()
    variant_info = RelationshipFrom("VariantInfo", "GenoInfo")
    hasInfo = RelationshipTo("Genotype", "HasInfo")
    
    @staticmethod
    def get_names():
        return ["id", "info"]
        
    def get_all(self):
        return [self.id, self.info]

class Genotype(StructuredNode):
    id = StringProperty(UniqueIndex=True, Required=True)
    hasInfo = RelationshipFrom("GenotypeInfo", "HasInfo")
    
    @staticmethod
    def get_names():
        return ["id"]
        
    def get_all(self):
        return [self.id]
    
class Chromosome(StructuredNode):
    id = StringProperty(UniqueIndex=True, Required=True)
    hasVariant = RelationshipTo("Variant", "HasVariant")
    
    @staticmethod
    def get_names():
        return ["id"]
        
    def get_all(self):
        return [self.id]

class Gene(StructuredNode):
    id = StringProperty(UniqueIndex=True, Required=True)
    
    @staticmethod
    def get_names():
        return ["id"]
        
    def get_all(self):
        return [self.id]



    