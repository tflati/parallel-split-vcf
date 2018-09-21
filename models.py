from neomodel import (config, StructuredNode, StringProperty, IntegerProperty, ArrayProperty, JSONProperty, FloatProperty, StructuredRel, RelationshipTo, RelationshipFrom)
config.DATABASE_URL = 'bolt://neo4j:password@localhost:7689'  # default

class Chromosome(StructuredNode):
    ID = StringProperty(UniqueIndex=True, Required=True)
    hasVariant = RelationshipTo("Variant", "HasVariant")
    
    @staticmethod
    def get_names():
        return ["ID"]
        
    def get_all(self):
        return [self.ID]
    
class HasVariant(StructuredRel):
    @staticmethod
    def get_names():
        return ["Chromosome", "Variant"]

class Variant(StructuredNode):
    ID = StringProperty(Required=True)
    
    chrom = StringProperty()
    pos = IntegerProperty()
    ref = StringProperty()
    alt = StringProperty()
    type = StringProperty()
    
    hasVariant = RelationshipFrom("Chromosome", "HasVariant")
    info = RelationshipTo("VariantInfo", "Info")
    
    @staticmethod
    def get_names():
        return ["ID", "chrom", "pos", "ref", "alt", "type"]
        
    def get_all(self):
        return [self.ID, self.chrom, self.pos, self.ref, self.alt, self.type]

class Info(StructuredRel):
    @staticmethod
    def get_names():
        return ["Variant", "VariantInfo"]

class VariantInfo(StructuredNode):
    ID = StringProperty(Required=True)
    
    qual = FloatProperty()
    filter = StringProperty()
    info = StringProperty()
    format = StringProperty()
    
    variant = RelationshipFrom("Variant", "Info")
    sampleInfo = RelationshipTo("Sample", "SampleInfo")
    
    @staticmethod
    def get_names():
        return ["ID", "qual", "filter", "info", "format"]
        
    def get_all(self):
        return [self.ID, self.qual, self.filter, self.info, self.format]

class SampleInfo(StructuredRel):
    info = StringProperty()
    
    @staticmethod
    def get_names():
        return ["VariantInfo", "Sample", "info"]

class Sample(StructuredNode):
    ID = StringProperty(UniqueIndex=True, Required=True)
    
    hasInfo = RelationshipFrom("VariantInfo", "SampleInfo")
    
    @staticmethod
    def get_names():
        return ["ID"]
        
    def get_all(self):
        return [self.ID]



    