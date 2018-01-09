create table if not exists partsmaster (
   "itemIdentifier" character varying(64),
   "itemUniqueIdentifier" character varying(64),
   "globalLifeCyclePhaseCode" character varying(24), --- Design, Preliminary, Prototype, Pilot, 
   --- Conditional, Production, Pending, Inactive, Unqualified, Disqualified, Obsolete, Other
   "globalLifeCyclePhaseCodeOther" character varying(24), -- same as above
   "globalProductTypeCode" character varying(64),
   "itemClassification" character varying(64),
   "revisionIdentifier" character varying(64),
   "versionIdentifer" character varying(64),
   "proprietaryProductFamily" character varying(512),
   "category" character varying(64),
   "globalProductUnitOfMeasureCode" character varying(64),
   "makeBuy" character varying(24), -- Make, Buy, Consigned, VendorManaged, Subcontracted, Unspecified, Other
   "makeBuyOther" character varying(24),
   "minimumShippableRevision" character varying(64),
   "revisionReleasedDate" timestamp,
   "revisionIncorporatedDate" timestamp,
   "isSerializationRequired" boolean, --- Yes, No
   "isCertificationRequired" boolean, --- Yes, No
   "ownerName" character varying(64),
   "ownerContactUniqueIdentifier" character varying(64),
   "isTopLevel" boolean, --- Yes, No
   "description" character varying(1024),
   
   primary key ("itemUniqueIdentifier")
);
