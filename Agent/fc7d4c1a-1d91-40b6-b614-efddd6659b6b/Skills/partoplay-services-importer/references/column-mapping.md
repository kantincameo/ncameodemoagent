# CSV Column Mapping

Services CSVs come from many different systems (spreadsheets, POS exports, booking tools), so
column headers are never standardized. Before mapping rows to the target schema, resolve every
raw CSV header to a target field using the alias table below.

Matching is **case-insensitive** and **whitespace-insensitive** (ignore extra spaces,
underscores, and hyphens when comparing).

| Target Field | Accepted CSV Column Names (aliases) |
|---|---|
| `serviceId` | ServiceId, Service Id, SvcId, Id |
| `serviceCode` | ServiceCode, Service Code, Code, Svc Code, SvcCode |
| `serviceName` | ServiceName, Service Name, Name, Svc Name, SvcName, Service Title, Title |
| `serviceCategory` | Category, ServiceCategory, Service Category, Cat, Svc Category |
| `serviceSubCategory` | Sub Category, SubCategory, Sub-Category, ServiceSubCategory, Sub Cat, SubCat |
| `serviceKind` | ServiceType, Service Type, Type, Kind, ServiceKind, Svc Type |
| `onlineBookingEnabled` | OnlineBooking, Online Booking, Online Book, Booking, IsOnline, OnlineEnabled |
| `taxIncluded` | TaxIncluded, Tax Included, Tax Inc, IncludesTax, IsTaxIncluded |
| `taxGroup` | TaxGroup, Tax Group, Tax Grp, TaxGrp, TaxCategory |
| `durationMinutes` | ServiceLength, Service Length, Duration, DurationMinutes, Minutes, ServiceTime, Length, Time, Mins |
| `price` | Price, ServicePrice, Service Price, Cost, Rate, Amount |

Columns with no match in this table (e.g. an internal "Business Unit Name" column) are simply
ignored — they don't get mapped to anything and don't appear in the output.

**Mapping rules:**
1. For each raw CSV header, find the best match in the alias table.
2. If a header matches an alias, map all values in that column to the corresponding target
   field.
3. If a header has no match, ignore that column entirely.
4. If a target field has no matching column in the CSV, apply its default per the row-mapping
   rules below.
5. If two or more CSV columns resolve to the same target field, use the first one encountered
   and ignore the rest.
6. Log the resolved mapping as `CSV column "<raw>" → target field "<target>"` for every
   matched column, so the user can see how their file was interpreted.

## Row → JSON mapping rules

Using the resolved column mapping, produce one JSON record per row:

| Target Field | Rule |
|---|---|
| `id` | Generate a new UUID v4 |
| `businessId` | `""` unless the user has given you an actual business id to use |
| `serviceId` | Direct copy from mapped column; may be empty or null |
| `serviceCode` | Direct copy; may be empty or null |
| `serviceName` | Direct copy; **required** — row is invalid without it |
| `serviceKind` | Direct copy; may be blank or null |
| `serviceCategory` | Direct copy; may be blank or null |
| `serviceSubCategory` | Direct copy; may be blank or null |
| `isAddOn` | `false` unless the CSV or user indicates otherwise |
| `durationMinutes` | Parse as integer; empty/missing → `0` |
| `price` | Parse as number; empty/missing → `0` |
| `taxIncluded` | empty/missing → `null`; `"true"`/`"1"`/`"yes"` → `true`; else `false` |
| `taxGroup` | empty/missing → `null`; else direct copy as string |
| `onlineBookingEnabled` | `"true"`/`"1"`/`"yes"` → `true`; empty/missing → `true` (default); else `false` |
| `requiresResource` | `null` unless stated |
| `requiresProvider` | `null` unless stated |
| `resourceType` | `null` unless stated |
| `providerType` | `null` unless stated |
| `isActive` | `true` |
| `createdAt` | Current UTC timestamp, ISO 8601 |
| `updatedAt` | Same value as `createdAt` |
| `_etag` | `null` |
| `_ts` | `null` |

**Validation:** a row is only included in the output if `id` is a non-empty UUID and
`serviceName` is non-empty. Log and skip anything else, and report the skipped rows to the
user during Stage 5.
