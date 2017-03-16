from neomodel import (config, StructuredNode, StringProperty, IntegerProperty, ArrayProperty, JSONProperty, FloatProperty, StructuredRel, RelationshipTo, RelationshipFrom)
config.DATABASE_URL = 'bolt://neo4j:password@localhost:7689'  # default

class Chromosome(StructuredNode):
    id = StringProperty(UniqueIndex=True, Required=True)
    hasVariant = RelationshipTo("Variant", "HasVariant")
    
    @staticmethod
    def get_names():
        return ["id"]
        
    def get_all(self):
        return [self.id]
    
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
    
    hasVariant = RelationshipFrom("Chromosome", "HasVariant")
    info = RelationshipTo("VariantInfo", "Info")
    
    @staticmethod
    def get_names():
        return ["id", "chrom", "pos", "ref", "alt"]
        
    def get_all(self):
        return [self.id, self.chrom, self.pos, self.ref, self.alt]

class Info(StructuredRel):
    @staticmethod
    def get_names():
        return ["Variant", "VariantInfo"]

class VariantInfo(StructuredNode):
    id = StringProperty(Required=True)
    
    qual = FloatProperty()
    filter = StringProperty()
    info = StringProperty()
    
    variant = RelationshipFrom("Variant", "Info")
    sampleInfo = RelationshipTo("Sample", "SampleInfo")
    
    @staticmethod
    def get_names():
        return ["id", "qual", "filter", "info"]
        
    def get_all(self):
        return [self.id, self.qual, self.filter, self.info]

class SampleInfo(StructuredRel):
    info = JSONProperty()
    
    @staticmethod
    def get_names():
        return ["VariantInfo", "Sample", "info"]

class Sample(StructuredNode):
    id = StringProperty(UniqueIndex=True, Required=True)
    
    hasInfo = RelationshipFrom("VariantInfo", "SampleInfo")
    
    @staticmethod
    def get_names():
        return ["id"]
        
    def get_all(self):
        return [self.id]

# class HasInfo(StructuredRel):
#     @staticmethod
#     def get_names():
#         return ["GenotypeInfo", "Genotype"]

# class GenotypeInfo(StructuredNode):
#     id = StringProperty(Required=True)
#     
#     info = StringProperty()
#     variant_info = RelationshipFrom("VariantInfo", "GenoInfo")
#     hasInfo = RelationshipTo("Sample", "HasInfo")
#     
#     @staticmethod
#     def get_names():
#         return ["id", "info"]
#         
#     def get_all(self):
#         return [self.id, self.info]


    
# class Gene(StructuredNode):
#     id = StringProperty(UniqueIndex=True, Required=True)
#     
#     @staticmethod
#     def get_names():
#         return ["id"]
#         
#     def get_all(self):
#         return [self.id]



    