# Database Introspection — airport_air_quality

_Generated on 2025-08-18 20:39:29 UTC_  
**Host**: `localhost`  |  **Port**: `5433`  |  **Schema filter**: `public`

## Instance

| version |
| --- |
| PostgreSQL 15.4 (Debian 15.4-1.pgdg110+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 10.2.1-6) 10.2.1 20210110, 64-bit |

### Extensions

| extname | extversion | schema |
| --- | --- | --- |
| plpgsql | 1.0 | pg_catalog |
| postgis | 3.3.4 | public |
| uuid-ossp | 1.1 | public |

## Schemas

| schema |
| --- |
| public |

## Schema `public`

### Tables

| table_schema | table_name |
| --- | --- |
| public | spatial_ref_sys |
| public | temp_flights_etl |
| public | temp_weather_etl |

### Views

| table_schema | table_name |
| --- | --- |
| public | geography_columns |
| public | geometry_columns |

### Table `public.spatial_ref_sys`

**Columns**

| ordinal_position | column_name | data_type | udt_name | is_nullable | column_default |
| --- | --- | --- | --- | --- | --- |
| 1 | srid | integer | int4 | NO |  |
| 2 | auth_name | character varying | varchar | YES |  |
| 3 | auth_srid | integer | int4 | YES |  |
| 4 | srtext | character varying | varchar | YES |  |
| 5 | proj4text | character varying | varchar | YES |  |

**Primary Key**

| column_name | constraint_name |
| --- | --- |
| srid | spatial_ref_sys_pkey |

**Foreign Keys**

_(none)_

**Indexes**

| indexname | indexdef |
| --- | --- |
| spatial_ref_sys_pkey | CREATE UNIQUE INDEX spatial_ref_sys_pkey ON public.spatial_ref_sys USING btree (srid) |

### Table `public.temp_flights_etl`

**Columns**

| ordinal_position | column_name | data_type | udt_name | is_nullable | column_default |
| --- | --- | --- | --- | --- | --- |
| 1 | numero_vol | character varying | varchar | YES |  |
| 2 | date_vol | date | date | YES |  |
| 3 | heure_depart | time without time zone | time | YES |  |
| 4 | heure_arrivee | time without time zone | time | YES |  |
| 5 | distance_km | integer | int4 | YES |  |
| 6 | nb_passagers | integer | int4 | YES |  |
| 7 | fuel_kg | numeric | numeric | YES |  |
| 8 | airline_iata | character varying | varchar | YES |  |
| 9 | aircraft_type | character varying | varchar | YES |  |
| 10 | destination | character varying | varchar | YES |  |
| 11 | flight_type | character varying | varchar | YES |  |
| 12 | data_source | character varying | varchar | YES |  |
| 13 | imported_at | timestamp without time zone | timestamp | YES | CURRENT_TIMESTAMP |

**Primary Key**

_(none)_

**Foreign Keys**

_(none)_

**Indexes**

_(none)_

### Table `public.temp_weather_etl`

**Columns**

| ordinal_position | column_name | data_type | udt_name | is_nullable | column_default |
| --- | --- | --- | --- | --- | --- |
| 1 | station_id | character varying | varchar | YES |  |
| 2 | measurement_time | timestamp without time zone | timestamp | YES |  |
| 3 | temperature | numeric | numeric | YES |  |
| 4 | imported_at | timestamp without time zone | timestamp | YES | CURRENT_TIMESTAMP |

**Primary Key**

_(none)_

**Foreign Keys**

_(none)_

**Indexes**

_(none)_

### Geometry Columns (PostGIS)

_No geometry columns._

### Functions

| function_name | args |
| --- | --- |
| _postgis_deprecate | oldname text, newname text, version text |
| _postgis_index_extent | tbl regclass, col text |
| _postgis_join_selectivity | regclass, text, regclass, text, text |
| _postgis_pgsql_version |  |
| _postgis_scripts_pgsql_version |  |
| _postgis_selectivity | tbl regclass, att_name text, geom geometry, mode text |
| _postgis_stats | tbl regclass, att_name text, text |
| _st_3ddfullywithin | geom1 geometry, geom2 geometry, double precision |
| _st_3ddwithin | geom1 geometry, geom2 geometry, double precision |
| _st_3dintersects | geom1 geometry, geom2 geometry |
| _st_asgml | integer, geometry, integer, integer, text, text |
| _st_asx3d | integer, geometry, integer, integer, text |
| _st_bestsrid | geography |
| _st_bestsrid | geography, geography |
| _st_concavehull | param_inputgeom geometry |
| _st_contains | geom1 geometry, geom2 geometry |
| _st_containsproperly | geom1 geometry, geom2 geometry |
| _st_coveredby | geom1 geometry, geom2 geometry |
| _st_coveredby | geog1 geography, geog2 geography |
| _st_covers | geog1 geography, geog2 geography |
| _st_covers | geom1 geometry, geom2 geometry |
| _st_crosses | geom1 geometry, geom2 geometry |
| _st_dfullywithin | geom1 geometry, geom2 geometry, double precision |
| _st_distancetree | geography, geography |
| _st_distancetree | geography, geography, double precision, boolean |
| _st_distanceuncached | geography, geography, double precision, boolean |
| _st_distanceuncached | geography, geography |
| _st_distanceuncached | geography, geography, boolean |
| _st_dwithin | geog1 geography, geog2 geography, tolerance double precision, use_spheroid boolean |
| _st_dwithin | geom1 geometry, geom2 geometry, double precision |
| _st_dwithinuncached | geography, geography, double precision, boolean |
| _st_dwithinuncached | geography, geography, double precision |
| _st_equals | geom1 geometry, geom2 geometry |
| _st_expand | geography, double precision |
| _st_geomfromgml | text, integer |
| _st_intersects | geom1 geometry, geom2 geometry |
| _st_linecrossingdirection | line1 geometry, line2 geometry |
| _st_longestline | geom1 geometry, geom2 geometry |
| _st_maxdistance | geom1 geometry, geom2 geometry |
| _st_orderingequals | geom1 geometry, geom2 geometry |
| _st_overlaps | geom1 geometry, geom2 geometry |
| _st_pointoutside | geography |
| _st_sortablehash | geom geometry |
| _st_touches | geom1 geometry, geom2 geometry |
| _st_voronoi | g1 geometry, clip geometry, tolerance double precision, return_polygons boolean |
| _st_within | geom1 geometry, geom2 geometry |
| addauth | text |
| addgeometrycolumn | schema_name character varying, table_name character varying, column_name character varying, new_srid integer, new_type character varying, new_dim integer, use_typmod boolean |
| addgeometrycolumn | table_name character varying, column_name character varying, new_srid integer, new_type character varying, new_dim integer, use_typmod boolean |
| addgeometrycolumn | catalog_name character varying, schema_name character varying, table_name character varying, column_name character varying, new_srid_in integer, new_type character varying, new_dim integer, use_typmod boolean |
| box | geometry |
| box | box3d |
| box2d | geometry |
| box2d | box3d |
| box2d_in | cstring |
| box2d_out | box2d |
| box2df_in | cstring |
| box2df_out | box2df |
| box3d | geometry |
| box3d | box2d |
| box3d_in | cstring |
| box3d_out | box3d |
| box3dtobox | box3d |
| bytea | geometry |
| bytea | geography |
| calculate_phase_duration |  |
| checkauth | text, text |
| checkauth | text, text, text |
| checkauthtrigger |  |
| contains_2d | geometry, box2df |
| contains_2d | box2df, geometry |
| contains_2d | box2df, box2df |
| disablelongtransactions |  |
| dropgeometrycolumn | catalog_name character varying, schema_name character varying, table_name character varying, column_name character varying |
| dropgeometrycolumn | table_name character varying, column_name character varying |
| dropgeometrycolumn | schema_name character varying, table_name character varying, column_name character varying |
| dropgeometrytable | schema_name character varying, table_name character varying |
| dropgeometrytable | table_name character varying |
| dropgeometrytable | catalog_name character varying, schema_name character varying, table_name character varying |
| enablelongtransactions |  |
| equals | geom1 geometry, geom2 geometry |
| find_srid | character varying, character varying, character varying |
| geog_brin_inclusion_add_value | internal, internal, internal, internal |
| geography | bytea |
| geography | geography, integer, boolean |
| geography | geometry |
| geography_analyze | internal |
| geography_cmp | geography, geography |
| geography_distance_knn | geography, geography |
| geography_eq | geography, geography |
| geography_ge | geography, geography |
| geography_gist_compress | internal |
| geography_gist_consistent | internal, geography, integer |
| geography_gist_decompress | internal |
| geography_gist_distance | internal, geography, integer |
| geography_gist_penalty | internal, internal, internal |
| geography_gist_picksplit | internal, internal |
| geography_gist_same | box2d, box2d, internal |
| geography_gist_union | bytea, internal |
| geography_gt | geography, geography |
| geography_in | cstring, oid, integer |
| geography_le | geography, geography |
| geography_lt | geography, geography |
| geography_out | geography |
| geography_overlaps | geography, geography |
| geography_recv | internal, oid, integer |
| geography_send | geography |
| geography_spgist_choose_nd | internal, internal |
| geography_spgist_compress_nd | internal |
| geography_spgist_config_nd | internal, internal |
| geography_spgist_inner_consistent_nd | internal, internal |
| geography_spgist_leaf_consistent_nd | internal, internal |
| geography_spgist_picksplit_nd | internal, internal |
| geography_typmod_in | cstring[] |
| geography_typmod_out | integer |
| geom2d_brin_inclusion_add_value | internal, internal, internal, internal |
| geom3d_brin_inclusion_add_value | internal, internal, internal, internal |
| geom4d_brin_inclusion_add_value | internal, internal, internal, internal |
| geometry | geography |
| geometry | bytea |
| geometry | text |
| geometry | polygon |
| geometry | box3d |
| geometry | box2d |
| geometry | path |
| geometry | point |
| geometry | geometry, integer, boolean |
| geometry_above | geom1 geometry, geom2 geometry |
| geometry_analyze | internal |
| geometry_below | geom1 geometry, geom2 geometry |
| geometry_cmp | geom1 geometry, geom2 geometry |
| geometry_contained_3d | geom1 geometry, geom2 geometry |
| geometry_contains | geom1 geometry, geom2 geometry |
| geometry_contains_3d | geom1 geometry, geom2 geometry |
| geometry_contains_nd | geometry, geometry |
| geometry_distance_box | geom1 geometry, geom2 geometry |
| geometry_distance_centroid | geom1 geometry, geom2 geometry |
| geometry_distance_centroid_nd | geometry, geometry |
| geometry_distance_cpa | geometry, geometry |
| geometry_eq | geom1 geometry, geom2 geometry |
| geometry_ge | geom1 geometry, geom2 geometry |
| geometry_gist_compress_2d | internal |
| geometry_gist_compress_nd | internal |
| geometry_gist_consistent_2d | internal, geometry, integer |
| geometry_gist_consistent_nd | internal, geometry, integer |
| geometry_gist_decompress_2d | internal |
| geometry_gist_decompress_nd | internal |
| geometry_gist_distance_2d | internal, geometry, integer |
| geometry_gist_distance_nd | internal, geometry, integer |
| geometry_gist_penalty_2d | internal, internal, internal |
| geometry_gist_penalty_nd | internal, internal, internal |
| geometry_gist_picksplit_2d | internal, internal |
| geometry_gist_picksplit_nd | internal, internal |
| geometry_gist_same_2d | geom1 geometry, geom2 geometry, internal |
| geometry_gist_same_nd | geometry, geometry, internal |
| geometry_gist_sortsupport_2d | internal |
| geometry_gist_union_2d | bytea, internal |
| geometry_gist_union_nd | bytea, internal |
| geometry_gt | geom1 geometry, geom2 geometry |
| geometry_hash | geometry |
| geometry_in | cstring |
| geometry_le | geom1 geometry, geom2 geometry |
| geometry_left | geom1 geometry, geom2 geometry |
| geometry_lt | geom1 geometry, geom2 geometry |
| geometry_out | geometry |
| geometry_overabove | geom1 geometry, geom2 geometry |
| geometry_overbelow | geom1 geometry, geom2 geometry |
| geometry_overlaps | geom1 geometry, geom2 geometry |
| geometry_overlaps_3d | geom1 geometry, geom2 geometry |
| geometry_overlaps_nd | geometry, geometry |
| geometry_overleft | geom1 geometry, geom2 geometry |
| geometry_overright | geom1 geometry, geom2 geometry |
| geometry_recv | internal |
| geometry_right | geom1 geometry, geom2 geometry |
| geometry_same | geom1 geometry, geom2 geometry |
| geometry_same_3d | geom1 geometry, geom2 geometry |
| geometry_same_nd | geometry, geometry |
| geometry_send | geometry |
| geometry_sortsupport | internal |
| geometry_spgist_choose_2d | internal, internal |
| geometry_spgist_choose_3d | internal, internal |
| geometry_spgist_choose_nd | internal, internal |
| geometry_spgist_compress_2d | internal |
| geometry_spgist_compress_3d | internal |
| geometry_spgist_compress_nd | internal |
| geometry_spgist_config_2d | internal, internal |
| geometry_spgist_config_3d | internal, internal |
| geometry_spgist_config_nd | internal, internal |
| geometry_spgist_inner_consistent_2d | internal, internal |
| geometry_spgist_inner_consistent_3d | internal, internal |
| geometry_spgist_inner_consistent_nd | internal, internal |
| geometry_spgist_leaf_consistent_2d | internal, internal |
| geometry_spgist_leaf_consistent_3d | internal, internal |
| geometry_spgist_leaf_consistent_nd | internal, internal |
| geometry_spgist_picksplit_2d | internal, internal |
| geometry_spgist_picksplit_3d | internal, internal |
| geometry_spgist_picksplit_nd | internal, internal |
| geometry_typmod_in | cstring[] |
| geometry_typmod_out | integer |
| geometry_within | geom1 geometry, geom2 geometry |
| geometry_within_nd | geometry, geometry |
| geometrytype | geometry |
| geometrytype | geography |
| geomfromewkb | bytea |
| geomfromewkt | text |
| get_proj4_from_srid | integer |
| gettransactionid |  |
| gidx_in | cstring |
| gidx_out | gidx |
| gserialized_gist_joinsel_2d | internal, oid, internal, smallint |
| gserialized_gist_joinsel_nd | internal, oid, internal, smallint |
| gserialized_gist_sel_2d | internal, oid, internal, integer |
| gserialized_gist_sel_nd | internal, oid, internal, integer |
| is_contained_2d | geometry, box2df |
| is_contained_2d | box2df, box2df |
| is_contained_2d | box2df, geometry |
| json | geometry |
| jsonb | geometry |
| lockrow | text, text, text, text |
| lockrow | text, text, text, text, timestamp without time zone |
| lockrow | text, text, text, timestamp without time zone |
| lockrow | text, text, text |
| longtransactionsenabled |  |
| overlaps_2d | box2df, box2df |
| overlaps_2d | box2df, geometry |
| overlaps_2d | geometry, box2df |
| overlaps_geog | geography, gidx |
| overlaps_geog | gidx, geography |
| overlaps_geog | gidx, gidx |
| overlaps_nd | geometry, gidx |
| overlaps_nd | gidx, gidx |
| overlaps_nd | gidx, geometry |
| path | geometry |
| pgis_asflatgeobuf_finalfn | internal |
| pgis_asflatgeobuf_transfn | internal, anyelement, boolean, text |
| pgis_asflatgeobuf_transfn | internal, anyelement |
| pgis_asflatgeobuf_transfn | internal, anyelement, boolean |
| pgis_asgeobuf_finalfn | internal |
| pgis_asgeobuf_transfn | internal, anyelement |
| pgis_asgeobuf_transfn | internal, anyelement, text |
| pgis_asmvt_combinefn | internal, internal |
| pgis_asmvt_deserialfn | bytea, internal |
| pgis_asmvt_finalfn | internal |
| pgis_asmvt_serialfn | internal |
| pgis_asmvt_transfn | internal, anyelement, text, integer, text, text |
| pgis_asmvt_transfn | internal, anyelement |
| pgis_asmvt_transfn | internal, anyelement, text |
| pgis_asmvt_transfn | internal, anyelement, text, integer, text |
| pgis_asmvt_transfn | internal, anyelement, text, integer |
| pgis_geometry_accum_transfn | internal, geometry, double precision, integer |
| pgis_geometry_accum_transfn | internal, geometry, double precision |
| pgis_geometry_accum_transfn | internal, geometry |
| pgis_geometry_clusterintersecting_finalfn | internal |
| pgis_geometry_clusterwithin_finalfn | internal |
| pgis_geometry_collect_finalfn | internal |
| pgis_geometry_makeline_finalfn | internal |
| pgis_geometry_polygonize_finalfn | internal |
| pgis_geometry_union_parallel_combinefn | internal, internal |
| pgis_geometry_union_parallel_deserialfn | bytea, internal |
| pgis_geometry_union_parallel_finalfn | internal |
| pgis_geometry_union_parallel_serialfn | internal |
| pgis_geometry_union_parallel_transfn | internal, geometry, double precision |
| pgis_geometry_union_parallel_transfn | internal, geometry |
| point | geometry |
| polygon | geometry |
| populate_geometry_columns | tbl_oid oid, use_typmod boolean |
| populate_geometry_columns | use_typmod boolean |
| postgis_addbbox | geometry |
| postgis_cache_bbox |  |
| postgis_constraint_dims | geomschema text, geomtable text, geomcolumn text |
| postgis_constraint_srid | geomschema text, geomtable text, geomcolumn text |
| postgis_constraint_type | geomschema text, geomtable text, geomcolumn text |
| postgis_dropbbox | geometry |
| postgis_extensions_upgrade |  |
| postgis_full_version |  |
| postgis_geos_noop | geometry |
| postgis_geos_version |  |
| postgis_getbbox | geometry |
| postgis_hasbbox | geometry |
| postgis_index_supportfn | internal |
| postgis_lib_build_date |  |
| postgis_lib_revision |  |
| postgis_lib_version |  |
| postgis_libjson_version |  |
| postgis_liblwgeom_version |  |
| postgis_libprotobuf_version |  |
| postgis_libxml_version |  |
| postgis_noop | geometry |
| postgis_proj_version |  |
| postgis_scripts_build_date |  |
| postgis_scripts_installed |  |
| postgis_scripts_released |  |
| postgis_svn_version |  |
| postgis_transform_geometry | geom geometry, text, text, integer |
| postgis_type_name | geomname character varying, coord_dimension integer, use_new_name boolean |
| postgis_typmod_dims | integer |
| postgis_typmod_srid | integer |
| postgis_typmod_type | integer |
| postgis_version |  |
| postgis_wagyu_version |  |
| spheroid_in | cstring |
| spheroid_out | spheroid |
| st_3dclosestpoint | geom1 geometry, geom2 geometry |
| st_3ddfullywithin | geom1 geometry, geom2 geometry, double precision |
| st_3ddistance | geom1 geometry, geom2 geometry |
| st_3ddwithin | geom1 geometry, geom2 geometry, double precision |
| st_3dextent | geometry |
| st_3dintersects | geom1 geometry, geom2 geometry |
| st_3dlength | geometry |
| st_3dlineinterpolatepoint | geometry, double precision |
| st_3dlongestline | geom1 geometry, geom2 geometry |
| st_3dmakebox | geom1 geometry, geom2 geometry |
| st_3dmaxdistance | geom1 geometry, geom2 geometry |
| st_3dperimeter | geometry |
| st_3dshortestline | geom1 geometry, geom2 geometry |
| st_addmeasure | geometry, double precision, double precision |
| st_addpoint | geom1 geometry, geom2 geometry |
| st_addpoint | geom1 geometry, geom2 geometry, integer |
| st_affine | geometry, double precision, double precision, double precision, double precision, double precision, double precision, double precision, double precision, double precision, double precision, double precision, double precision |
| st_affine | geometry, double precision, double precision, double precision, double precision, double precision, double precision |
| st_angle | line1 geometry, line2 geometry |
| st_angle | pt1 geometry, pt2 geometry, pt3 geometry, pt4 geometry |
| st_area | text |
| st_area | geog geography, use_spheroid boolean |
| st_area | geometry |
| st_area2d | geometry |
| st_asbinary | geometry, text |
| st_asbinary | geography, text |
| st_asbinary | geometry |
| st_asbinary | geography |
| st_asencodedpolyline | geom geometry, nprecision integer |
| st_asewkb | geometry, text |
| st_asewkb | geometry |
| st_asewkt | geometry, integer |
| st_asewkt | geography, integer |
| st_asewkt | text |
| st_asewkt | geography |
| st_asewkt | geometry |
| st_asflatgeobuf | anyelement, boolean |
| st_asflatgeobuf | anyelement |
| st_asflatgeobuf | anyelement, boolean, text |
| st_asgeobuf | anyelement |
| st_asgeobuf | anyelement, text |
| st_asgeojson | geog geography, maxdecimaldigits integer, options integer |
| st_asgeojson | text |
| st_asgeojson | r record, geom_column text, maxdecimaldigits integer, pretty_bool boolean |
| st_asgeojson | geom geometry, maxdecimaldigits integer, options integer |
| st_asgml | geom geometry, maxdecimaldigits integer, options integer |
| st_asgml | version integer, geom geometry, maxdecimaldigits integer, options integer, nprefix text, id text |
| st_asgml | text |
| st_asgml | geog geography, maxdecimaldigits integer, options integer, nprefix text, id text |
| st_asgml | version integer, geog geography, maxdecimaldigits integer, options integer, nprefix text, id text |
| st_ashexewkb | geometry, text |
| st_ashexewkb | geometry |
| st_askml | geom geometry, maxdecimaldigits integer, nprefix text |
| st_askml | geog geography, maxdecimaldigits integer, nprefix text |
| st_askml | text |
| st_aslatlontext | geom geometry, tmpl text |
| st_asmarc21 | geom geometry, format text |
| st_asmvt | anyelement |
| st_asmvt | anyelement, text, integer, text, text |
| st_asmvt | anyelement, text, integer, text |
| st_asmvt | anyelement, text, integer |
| st_asmvt | anyelement, text |
| st_asmvtgeom | geom geometry, bounds box2d, extent integer, buffer integer, clip_geom boolean |
| st_assvg | geog geography, rel integer, maxdecimaldigits integer |
| st_assvg | text |
| st_assvg | geom geometry, rel integer, maxdecimaldigits integer |
| st_astext | geometry |
| st_astext | geography, integer |
| st_astext | text |
| st_astext | geography |
| st_astext | geometry, integer |
| st_astwkb | geom geometry, prec integer, prec_z integer, prec_m integer, with_sizes boolean, with_boxes boolean |
| st_astwkb | geom geometry[], ids bigint[], prec integer, prec_z integer, prec_m integer, with_sizes boolean, with_boxes boolean |
| st_asx3d | geom geometry, maxdecimaldigits integer, options integer |
| st_azimuth | geog1 geography, geog2 geography |
| st_azimuth | geom1 geometry, geom2 geometry |
| st_bdmpolyfromtext | text, integer |
| st_bdpolyfromtext | text, integer |
| st_boundary | geometry |
| st_boundingdiagonal | geom geometry, fits boolean |
| st_box2dfromgeohash | text, integer |
| st_buffer | geography, double precision |
| st_buffer | geom geometry, radius double precision, options text |
| st_buffer | text, double precision, integer |
| st_buffer | geography, double precision, integer |
| st_buffer | geography, double precision, text |
| st_buffer | text, double precision |
| st_buffer | geom geometry, radius double precision, quadsegs integer |
| st_buffer | text, double precision, text |
| st_buildarea | geometry |
| st_centroid | geometry |
| st_centroid | text |
| st_centroid | geography, use_spheroid boolean |
| st_chaikinsmoothing | geometry, integer, boolean |
| st_cleangeometry | geometry |
| st_clipbybox2d | geom geometry, box box2d |
| st_closestpoint | geom1 geometry, geom2 geometry |
| st_closestpointofapproach | geometry, geometry |
| st_clusterdbscan | geometry, eps double precision, minpoints integer |
| st_clusterintersecting | geometry |
| st_clusterintersecting | geometry[] |
| st_clusterkmeans | geom geometry, k integer, max_radius double precision |
| st_clusterwithin | geometry[], double precision |
| st_clusterwithin | geometry, double precision |
| st_collect | geometry |
| st_collect | geom1 geometry, geom2 geometry |
| st_collect | geometry[] |
| st_collectionextract | geometry |
| st_collectionextract | geometry, integer |
| st_collectionhomogenize | geometry |
| st_combinebbox | box3d, box3d |
| st_combinebbox | box3d, geometry |
| st_combinebbox | box2d, geometry |
| st_concavehull | param_geom geometry, param_pctconvex double precision, param_allow_holes boolean |
| st_contains | geom1 geometry, geom2 geometry |
| st_containsproperly | geom1 geometry, geom2 geometry |
| st_convexhull | geometry |
| st_coorddim | geometry geometry |
| st_coveredby | text, text |
| st_coveredby | geom1 geometry, geom2 geometry |
| st_coveredby | geog1 geography, geog2 geography |
| st_covers | text, text |
| st_covers | geog1 geography, geog2 geography |
| st_covers | geom1 geometry, geom2 geometry |
| st_cpawithin | geometry, geometry, double precision |
| st_crosses | geom1 geometry, geom2 geometry |
| st_curvetoline | geom geometry, tol double precision, toltype integer, flags integer |
| st_delaunaytriangles | g1 geometry, tolerance double precision, flags integer |
| st_dfullywithin | geom1 geometry, geom2 geometry, double precision |
| st_difference | geom1 geometry, geom2 geometry, gridsize double precision |
| st_dimension | geometry |
| st_disjoint | geom1 geometry, geom2 geometry |
| st_distance | geom1 geometry, geom2 geometry |
| st_distance | text, text |
| st_distance | geog1 geography, geog2 geography, use_spheroid boolean |
| st_distancecpa | geometry, geometry |
| st_distancesphere | geom1 geometry, geom2 geometry, radius double precision |
| st_distancesphere | geom1 geometry, geom2 geometry |
| st_distancespheroid | geom1 geometry, geom2 geometry |
| st_distancespheroid | geom1 geometry, geom2 geometry, spheroid |
| st_dump | geometry |
| st_dumppoints | geometry |
| st_dumprings | geometry |
| st_dumpsegments | geometry |
| st_dwithin | geom1 geometry, geom2 geometry, double precision |
| st_dwithin | text, text, double precision |
| st_dwithin | geog1 geography, geog2 geography, tolerance double precision, use_spheroid boolean |
| st_endpoint | geometry |
| st_envelope | geometry |
| st_equals | geom1 geometry, geom2 geometry |
| st_estimatedextent | text, text, text |
| st_estimatedextent | text, text, text, boolean |
| st_estimatedextent | text, text |
| st_expand | box3d, double precision |
| st_expand | box box3d, dx double precision, dy double precision, dz double precision |
| st_expand | box2d, double precision |
| st_expand | box box2d, dx double precision, dy double precision |
| st_expand | geom geometry, dx double precision, dy double precision, dz double precision, dm double precision |
| st_expand | geometry, double precision |
| st_extent | geometry |
| st_exteriorring | geometry |
| st_filterbym | geometry, double precision, double precision, boolean |
| st_findextent | text, text, text |
| st_findextent | text, text |
| st_flipcoordinates | geometry |
| st_force2d | geometry |
| st_force3d | geom geometry, zvalue double precision |
| st_force3dm | geom geometry, mvalue double precision |
| st_force3dz | geom geometry, zvalue double precision |
| st_force4d | geom geometry, zvalue double precision, mvalue double precision |
| st_forcecollection | geometry |
| st_forcecurve | geometry |
| st_forcepolygonccw | geometry |
| st_forcepolygoncw | geometry |
| st_forcerhr | geometry |
| st_forcesfs | geometry, version text |
| st_forcesfs | geometry |
| st_frechetdistance | geom1 geometry, geom2 geometry, double precision |
| st_fromflatgeobuf | anyelement, bytea |
| st_fromflatgeobuftotable | text, text, bytea |
| st_generatepoints | area geometry, npoints integer |
| st_generatepoints | area geometry, npoints integer, seed integer |
| st_geogfromtext | text |
| st_geogfromwkb | bytea |
| st_geographyfromtext | text |
| st_geohash | geom geometry, maxchars integer |
| st_geohash | geog geography, maxchars integer |
| st_geomcollfromtext | text, integer |
| st_geomcollfromtext | text |
| st_geomcollfromwkb | bytea |
| st_geomcollfromwkb | bytea, integer |
| st_geometricmedian | g geometry, tolerance double precision, max_iter integer, fail_if_not_converged boolean |
| st_geometryfromtext | text, integer |
| st_geometryfromtext | text |
| st_geometryn | geometry, integer |
| st_geometrytype | geometry |
| st_geomfromewkb | bytea |
| st_geomfromewkt | text |
| st_geomfromgeohash | text, integer |
| st_geomfromgeojson | text |
| st_geomfromgeojson | json |
| st_geomfromgeojson | jsonb |
| st_geomfromgml | text |
| st_geomfromgml | text, integer |
| st_geomfromkml | text |
| st_geomfrommarc21 | marc21xml text |
| st_geomfromtext | text |
| st_geomfromtext | text, integer |
| st_geomfromtwkb | bytea |
| st_geomfromwkb | bytea |
| st_geomfromwkb | bytea, integer |
| st_gmltosql | text, integer |
| st_gmltosql | text |
| st_hasarc | geometry geometry |
| st_hausdorffdistance | geom1 geometry, geom2 geometry |
| st_hausdorffdistance | geom1 geometry, geom2 geometry, double precision |
| st_hexagon | size double precision, cell_i integer, cell_j integer, origin geometry |
| st_hexagongrid | size double precision, bounds geometry, OUT geom geometry, OUT i integer, OUT j integer |
| st_interiorringn | geometry, integer |
| st_interpolatepoint | line geometry, point geometry |
| st_intersection | geom1 geometry, geom2 geometry, gridsize double precision |
| st_intersection | geography, geography |
| st_intersection | text, text |
| st_intersects | geog1 geography, geog2 geography |
| st_intersects | geom1 geometry, geom2 geometry |
| st_intersects | text, text |
| st_isclosed | geometry |
| st_iscollection | geometry |
| st_isempty | geometry |
| st_ispolygonccw | geometry |
| st_ispolygoncw | geometry |
| st_isring | geometry |
| st_issimple | geometry |
| st_isvalid | geometry, integer |
| st_isvalid | geometry |
| st_isvaliddetail | geom geometry, flags integer |
| st_isvalidreason | geometry, integer |
| st_isvalidreason | geometry |
| st_isvalidtrajectory | geometry |
| st_length | geog geography, use_spheroid boolean |
| st_length | geometry |
| st_length | text |
| st_length2d | geometry |
| st_length2dspheroid | geometry, spheroid |
| st_lengthspheroid | geometry, spheroid |
| st_letters | letters text, font json |
| st_linecrossingdirection | line1 geometry, line2 geometry |
| st_linefromencodedpolyline | txtin text, nprecision integer |
| st_linefrommultipoint | geometry |
| st_linefromtext | text |
| st_linefromtext | text, integer |
| st_linefromwkb | bytea |
| st_linefromwkb | bytea, integer |
| st_lineinterpolatepoint | geometry, double precision |
| st_lineinterpolatepoints | geometry, double precision, repeat boolean |
| st_linelocatepoint | geom1 geometry, geom2 geometry |
| st_linemerge | geometry, boolean |
| st_linemerge | geometry |
| st_linestringfromwkb | bytea |
| st_linestringfromwkb | bytea, integer |
| st_linesubstring | geometry, double precision, double precision |
| st_linetocurve | geometry geometry |
| st_locatealong | geometry geometry, measure double precision, leftrightoffset double precision |
| st_locatebetween | geometry geometry, frommeasure double precision, tomeasure double precision, leftrightoffset double precision |
| st_locatebetweenelevations | geometry geometry, fromelevation double precision, toelevation double precision |
| st_longestline | geom1 geometry, geom2 geometry |
| st_m | geometry |
| st_makebox2d | geom1 geometry, geom2 geometry |
| st_makeenvelope | double precision, double precision, double precision, double precision, integer |
| st_makeline | geometry |
| st_makeline | geom1 geometry, geom2 geometry |
| st_makeline | geometry[] |
| st_makepoint | double precision, double precision |
| st_makepoint | double precision, double precision, double precision, double precision |
| st_makepoint | double precision, double precision, double precision |
| st_makepointm | double precision, double precision, double precision |
| st_makepolygon | geometry, geometry[] |
| st_makepolygon | geometry |
| st_makevalid | geom geometry, params text |
| st_makevalid | geometry |
| st_maxdistance | geom1 geometry, geom2 geometry |
| st_maximuminscribedcircle | geometry, OUT center geometry, OUT nearest geometry, OUT radius double precision |
| st_memcollect | geometry |
| st_memsize | geometry |
| st_memunion | geometry |
| st_minimumboundingcircle | inputgeom geometry, segs_per_quarter integer |
| st_minimumboundingradius | geometry, OUT center geometry, OUT radius double precision |
| st_minimumclearance | geometry |
| st_minimumclearanceline | geometry |
| st_mlinefromtext | text |
| st_mlinefromtext | text, integer |
| st_mlinefromwkb | bytea |
| st_mlinefromwkb | bytea, integer |
| st_mpointfromtext | text, integer |
| st_mpointfromtext | text |
| st_mpointfromwkb | bytea, integer |
| st_mpointfromwkb | bytea |
| st_mpolyfromtext | text, integer |
| st_mpolyfromtext | text |
| st_mpolyfromwkb | bytea, integer |
| st_mpolyfromwkb | bytea |
| st_multi | geometry |
| st_multilinefromwkb | bytea |
| st_multilinestringfromtext | text |
| st_multilinestringfromtext | text, integer |
| st_multipointfromtext | text |
| st_multipointfromwkb | bytea, integer |
| st_multipointfromwkb | bytea |
| st_multipolyfromwkb | bytea |
| st_multipolyfromwkb | bytea, integer |
| st_multipolygonfromtext | text |
| st_multipolygonfromtext | text, integer |
| st_ndims | geometry |
| st_node | g geometry |
| st_normalize | geom geometry |
| st_npoints | geometry |
| st_nrings | geometry |
| st_numgeometries | geometry |
| st_numinteriorring | geometry |
| st_numinteriorrings | geometry |
| st_numpatches | geometry |
| st_numpoints | geometry |
| st_offsetcurve | line geometry, distance double precision, params text |
| st_orderingequals | geom1 geometry, geom2 geometry |
| st_orientedenvelope | geometry |
| st_overlaps | geom1 geometry, geom2 geometry |
| st_patchn | geometry, integer |
| st_perimeter | geometry |
| st_perimeter | geog geography, use_spheroid boolean |
| st_perimeter2d | geometry |
| st_point | double precision, double precision |
| st_point | double precision, double precision, srid integer |
| st_pointfromgeohash | text, integer |
| st_pointfromtext | text, integer |
| st_pointfromtext | text |
| st_pointfromwkb | bytea |
| st_pointfromwkb | bytea, integer |
| st_pointinsidecircle | geometry, double precision, double precision, double precision |
| st_pointm | xcoordinate double precision, ycoordinate double precision, mcoordinate double precision, srid integer |
| st_pointn | geometry, integer |
| st_pointonsurface | geometry |
| st_points | geometry |
| st_pointz | xcoordinate double precision, ycoordinate double precision, zcoordinate double precision, srid integer |
| st_pointzm | xcoordinate double precision, ycoordinate double precision, zcoordinate double precision, mcoordinate double precision, srid integer |
| st_polyfromtext | text, integer |
| st_polyfromtext | text |
| st_polyfromwkb | bytea, integer |
| st_polyfromwkb | bytea |
| st_polygon | geometry, integer |
| st_polygonfromtext | text, integer |
| st_polygonfromtext | text |
| st_polygonfromwkb | bytea, integer |
| st_polygonfromwkb | bytea |
| st_polygonize | geometry |
| st_polygonize | geometry[] |
| st_project | geog geography, distance double precision, azimuth double precision |
| st_quantizecoordinates | g geometry, prec_x integer, prec_y integer, prec_z integer, prec_m integer |
| st_reduceprecision | geom geometry, gridsize double precision |
| st_relate | geom1 geometry, geom2 geometry |
| st_relate | geom1 geometry, geom2 geometry, text |
| st_relate | geom1 geometry, geom2 geometry, integer |
| st_relatematch | text, text |
| st_removepoint | geometry, integer |
| st_removerepeatedpoints | geom geometry, tolerance double precision |
| st_reverse | geometry |
| st_rotate | geometry, double precision, geometry |
| st_rotate | geometry, double precision, double precision, double precision |
| st_rotate | geometry, double precision |
| st_rotatex | geometry, double precision |
| st_rotatey | geometry, double precision |
| st_rotatez | geometry, double precision |
| st_scale | geometry, geometry |
| st_scale | geometry, double precision, double precision |
| st_scale | geometry, double precision, double precision, double precision |
| st_scale | geometry, geometry, origin geometry |
| st_scroll | geometry, geometry |
| st_segmentize | geometry, double precision |
| st_segmentize | geog geography, max_segment_length double precision |
| st_seteffectivearea | geometry, double precision, integer |
| st_setpoint | geometry, integer, geometry |
| st_setsrid | geog geography, srid integer |
| st_setsrid | geom geometry, srid integer |
| st_sharedpaths | geom1 geometry, geom2 geometry |
| st_shiftlongitude | geometry |
| st_shortestline | geom1 geometry, geom2 geometry |
| st_simplify | geometry, double precision |
| st_simplify | geometry, double precision, boolean |
| st_simplifypolygonhull | geom geometry, vertex_fraction double precision, is_outer boolean |
| st_simplifypreservetopology | geometry, double precision |
| st_simplifyvw | geometry, double precision |
| st_snap | geom1 geometry, geom2 geometry, double precision |
| st_snaptogrid | geom1 geometry, geom2 geometry, double precision, double precision, double precision, double precision |
| st_snaptogrid | geometry, double precision |
| st_snaptogrid | geometry, double precision, double precision, double precision, double precision |
| st_snaptogrid | geometry, double precision, double precision |
| st_split | geom1 geometry, geom2 geometry |
| st_square | size double precision, cell_i integer, cell_j integer, origin geometry |
| st_squaregrid | size double precision, bounds geometry, OUT geom geometry, OUT i integer, OUT j integer |
| st_srid | geom geometry |
| st_srid | geog geography |
| st_startpoint | geometry |
| st_subdivide | geom geometry, maxvertices integer, gridsize double precision |
| st_summary | geometry |
| st_summary | geography |
| st_swapordinates | geom geometry, ords cstring |
| st_symdifference | geom1 geometry, geom2 geometry, gridsize double precision |
| st_symmetricdifference | geom1 geometry, geom2 geometry |
| st_tileenvelope | zoom integer, x integer, y integer, bounds geometry, margin double precision |
| st_touches | geom1 geometry, geom2 geometry |
| st_transform | geometry, integer |
| st_transform | geom geometry, to_proj text |
| st_transform | geom geometry, from_proj text, to_srid integer |
| st_transform | geom geometry, from_proj text, to_proj text |
| st_translate | geometry, double precision, double precision, double precision |
| st_translate | geometry, double precision, double precision |
| st_transscale | geometry, double precision, double precision, double precision, double precision |
| st_triangulatepolygon | g1 geometry |
| st_unaryunion | geometry, gridsize double precision |
| st_union | geometry |
| st_union | geom1 geometry, geom2 geometry |
| st_union | geometry, gridsize double precision |
| st_union | geom1 geometry, geom2 geometry, gridsize double precision |
| st_union | geometry[] |
| st_voronoilines | g1 geometry, tolerance double precision, extend_to geometry |
| st_voronoipolygons | g1 geometry, tolerance double precision, extend_to geometry |
| st_within | geom1 geometry, geom2 geometry |
| st_wkbtosql | wkb bytea |
| st_wkttosql | text |
| st_wrapx | geom geometry, wrap double precision, move double precision |
| st_x | geometry |
| st_xmax | box3d |
| st_xmin | box3d |
| st_y | geometry |
| st_ymax | box3d |
| st_ymin | box3d |
| st_z | geometry |
| st_zmax | box3d |
| st_zmflag | geometry |
| st_zmin | box3d |
| text | geometry |
| unlockrows | text |
| update_modified_timestamp |  |
| updategeometrysrid | catalogn_name character varying, schema_name character varying, table_name character varying, column_name character varying, new_srid_in integer |
| updategeometrysrid | character varying, character varying, integer |
| updategeometrysrid | character varying, character varying, character varying, integer |
| uuid_generate_v1 |  |
| uuid_generate_v1mc |  |
| uuid_generate_v3 | namespace uuid, name text |
| uuid_generate_v4 |  |
| uuid_generate_v5 | namespace uuid, name text |
| uuid_nil |  |
| uuid_ns_dns |  |
| uuid_ns_oid |  |
| uuid_ns_url |  |
| uuid_ns_x500 |  |

