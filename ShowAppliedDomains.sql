create procedure ShowAppliedDomains @DOMAIN_NAME NVARCHAR(MAX)
as
--DECLARE @DOMAIN_NAME NVARCHAR(MAX);
--SET @DOMAIN_NAME = 'DES_cable_distribution_size_ug';

DECLARE @CLASS_DEFS TABLE
(
     Name nvarchar(max),
     Definition XML
)
SET NOCOUNT ON; --you need this to be able to avoid the not a sql query issue (pyodbc)
--Insert records to temporary record set
INSERT INTO @CLASS_DEFS
SELECT
  sde.gdb_items.Name,
  sde.gdb_items.Definition
FROM
-- Get the domain item's UUID.
((SELECT GDB_ITEMS.UUID AS UUID
  FROM sde.gdb_items INNER JOIN sde.gdb_itemtypes
  ON sde.gdb_items.Type = sde.gdb_itemtypes.UUID
  WHERE
    sde.gdb_items.Name = @DOMAIN_NAME AND
    sde.gdb_itemtypes.Name IN ('Coded Value Domain','Range Domain')) AS Domain

-- Find the relationships with the domain as the DestinationID.
INNER JOIN sde.gdb_itemrelationships
ON Domain.UUID = sde.gdb_itemrelationships.DestID)

-- Find the names of the origin items in the relationships.
INNER JOIN sde.gdb_items
ON Domain.UUID = sde.gdb_itemrelationships.DestID

-- Extract the field definitions.

SELECT
  ClassDefs.Name AS "Class Name",
  fieldDef.value('Name[1]', 'nvarchar(max)') AS "Field Name",
  NULL AS "Subtype Name"
FROM
  @CLASS_DEFS AS ClassDefs
CROSS APPLY
  Definition.nodes('/*/GPFieldInfoExs/GPFieldInfoEx') AS FieldDefs(fieldDef)
WHERE
  fieldDef.value('DomainName[1]', 'nvarchar(max)') = @DOMAIN_NAME

UNION

SELECT
  ClassDefs.Name AS "Class Name",
  fieldDef.value('FieldName[1]', 'nvarchar(max)') AS "Field Name",
  fieldDef.value('(../../SubtypeName)[1]', 'nvarchar(max)') AS "Subtype Name"
FROM
  @CLASS_DEFS AS ClassDefs
CROSS APPLY
   Definition.nodes('/*/Subtypes/Subtype/FieldInfos/SubtypeFieldInfo') AS FieldDefs(fieldDef)
WHERE
  fieldDef.value('DomainName[1]', 'nvarchar(max)') = @DOMAIN_NAME