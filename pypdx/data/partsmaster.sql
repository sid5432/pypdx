create table if not exists partsmaster (
   "itemidentifier" character varying(64),
   "itemuniqueidentifier" character varying(64),
   "globallifecyclephasecode" character varying(24), --- design, preliminary, prototype, pilot, 
   --- conditional, production, pending, inactive, unqualified, disqualified, obsolete, other
   "globallifecyclephasecodeother" character varying(24), -- same as above
   "globalproducttypecode" character varying(64),
   "itemclassification" character varying(64),
   "revisionidentifier" character varying(64),
   "versionidentifer" character varying(64),
   "proprietaryproductfamily" character varying(512),
   "category" character varying(64),
   "globalproductunitofmeasurecode" character varying(64),
   "makebuy" character varying(24), -- make, buy, consigned, vendormanaged, subcontracted, unspecified, other
   "makebuyother" character varying(24),
   "minimumshippablerevision" character varying(64),
   "revisionreleaseddate" timestamp with time zone,
   "revisionincorporateddate" timestamp with time zone,
   "isserializationrequired" boolean, --- yes, no
   "iscertificationrequired" boolean, --- yes, no
   "ownername" character varying(64),
   "ownercontactuniqueidentifier" character varying(64),
   "istoplevel" boolean, --- yes, no
   "description" character varying(1024),
   
   primary key ("itemuniqueidentifier")
);
