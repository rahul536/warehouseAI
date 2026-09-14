-- ============================================================
-- WarehouseAI - WMS Seed Data
-- File: 02_seed_wms_data.sql
-- ============================================================

BEGIN;

-- ============================================================
-- 1. WAREHOUSE / SITE
-- ============================================================

INSERT INTO warehouse_site_details (
    ws_warehouse_id,
    ws_site_id,
    ws_site_name,
    ws_description,
    ws_status,
    ws_address_line1,
    ws_city,
    ws_state,
    ws_country,
    ws_zip,
    ws_phone,
    ws_email
)
VALUES (
    'WH01',
    'SITE01',
    'Dubai Main Warehouse',
    'Main distribution warehouse for UAE operations',
    'ACTIVE',
    'Warehouse 12, Dubai Industrial Area',
    'Dubai',
    'Dubai',
    'UAE',
    '00000',
    '+971500000001',
    'wh01@warehouseai.local'
);


-- ============================================================
-- 2. STORAGE LOCATIONS
-- ============================================================

INSERT INTO storage_location_details (
    sl_warehouse_id,
    sl_site_id,
    sl_zone,
    sl_location_id,
    sl_status,
    sl_mixed_hu_allowed,
    sl_inventory_addition_allowed,
    sl_capacity_check_enabled,
    sl_allocation_enabled,
    sl_replenishment_enabled
)
VALUES

-- Receiving
('WH01','SITE01','RECEIVING','GR01',
 'ACTIVE',FALSE,TRUE,FALSE,FALSE,FALSE),

-- Bulk storage
('WH01','SITE01','STORAGE','BULK01',
 'ACTIVE',FALSE,TRUE,TRUE,TRUE,TRUE),

-- Picking area
('WH01','SITE01','PICKING','PICK01',
 'ACTIVE',FALSE,TRUE,TRUE,TRUE,TRUE),

-- Packing
('WH01','SITE01','PACKING','PACK01',
 'ACTIVE',TRUE,TRUE,FALSE,FALSE,FALSE),

-- Exit staging
('WH01','SITE01','EXIT','EXIT01',
 'ACTIVE',TRUE,TRUE,FALSE,FALSE,FALSE);


-- ============================================================
-- 3. STORAGE BINS
-- ============================================================

INSERT INTO storage_bin_details (
    sb_warehouse_id,
    sb_site_id,
    sb_zone,
    sb_location_id,
    sb_aisle_number,
    sb_rack_number,
    sb_bin_number_horizontal,
    sb_bin_number_vertical,
    sb_bin_status
)
VALUES

-- BULK01 / A01 / R01
('WH01','SITE01','STORAGE','BULK01','A01','R01','B01','01','OCCUPIED'),
('WH01','SITE01','STORAGE','BULK01','A01','R01','B02','01','OCCUPIED'),
('WH01','SITE01','STORAGE','BULK01','A01','R01','B03','01','OCCUPIED'),
('WH01','SITE01','STORAGE','BULK01','A01','R01','B04','01','EMPTY'),

-- A01 / R02
('WH01','SITE01','STORAGE','BULK01','A01','R02','B01','01','OCCUPIED'),
('WH01','SITE01','STORAGE','BULK01','A01','R02','B02','01','OCCUPIED'),
('WH01','SITE01','STORAGE','BULK01','A01','R02','B03','01','OCCUPIED'),
('WH01','SITE01','STORAGE','BULK01','A01','R02','B04','01','EMPTY'),

-- A02 / R01
('WH01','SITE01','STORAGE','BULK01','A02','R01','B01','01','OCCUPIED'),
('WH01','SITE01','STORAGE','BULK01','A02','R01','B02','01','OCCUPIED'),
('WH01','SITE01','STORAGE','BULK01','A02','R01','B03','01','EMPTY'),
('WH01','SITE01','STORAGE','BULK01','A02','R01','B04','01','EMPTY'),

-- PICK01
('WH01','SITE01','PICKING','PICK01','P01','R01','B01','01','OCCUPIED'),
('WH01','SITE01','PICKING','PICK01','P01','R01','B02','01','OCCUPIED'),
('WH01','SITE01','PICKING','PICK01','P01','R01','B03','01','EMPTY');


-- ============================================================
-- 4. ITEMS
-- ============================================================

INSERT INTO item_details (
    it_warehouse_id,
    it_site_id,
    it_item_id,
    it_item_name,
    it_description,
    it_uom,
    it_unit_weight_kg,
    it_unit_volume_m3,
    it_bbd_mandatory,
    it_batch_mandatory,
    it_status
)
VALUES

('WH01','SITE01','ITEM001',
 'Wireless Mouse',
 'Standard wireless computer mouse',
 'EA',0.120,0.00080,FALSE,FALSE,'ACTIVE'),

('WH01','SITE01','ITEM002',
 'USB Keyboard',
 'USB keyboard',
 'EA',0.450,0.00200,FALSE,FALSE,'ACTIVE'),

('WH01','SITE01','ITEM003',
 '27 Inch Monitor',
 '27 inch LED monitor',
 'EA',4.500,0.03000,FALSE,FALSE,'ACTIVE'),

('WH01','SITE01','ITEM004',
 'Laptop Stand',
 'Adjustable aluminium laptop stand',
 'EA',1.100,0.00400,FALSE,FALSE,'ACTIVE'),

('WH01','SITE01','ITEM005',
 'HDMI Cable',
 'High speed HDMI cable',
 'EA',0.150,0.00050,FALSE,FALSE,'ACTIVE'),

('WH01','SITE01','ITEM006',
 'Office Chair',
 'Ergonomic office chair',
 'EA',12.000,0.08000,FALSE,FALSE,'ACTIVE'),

('WH01','SITE01','ITEM007',
 'Printer Toner',
 'Laser printer toner cartridge',
 'EA',0.800,0.00300,FALSE,TRUE,'ACTIVE'),

('WH01','SITE01','ITEM008',
 'Hand Sanitizer',
 '500ml hand sanitizer',
 'EA',0.550,0.00100,TRUE,TRUE,'ACTIVE'),

('WH01','SITE01','ITEM009',
 'Cleaning Spray',
 'Multi-purpose cleaning spray',
 'EA',0.700,0.00120,TRUE,FALSE,'ACTIVE'),

('WH01','SITE01','ITEM010',
 'Packing Tape',
 'Industrial packing tape',
 'EA',0.250,0.00070,FALSE,FALSE,'ACTIVE'),

('WH01','SITE01','ITEM011',
 'Cardboard Box Small',
 'Small shipping carton',
 'EA',0.300,0.00500,FALSE,FALSE,'ACTIVE'),

('WH01','SITE01','ITEM012',
 'Cardboard Box Large',
 'Large shipping carton',
 'EA',0.600,0.02000,FALSE,FALSE,'ACTIVE'),

('WH01','SITE01','ITEM013',
 'Coffee Beans 1kg',
 'Roasted coffee beans',
 'EA',1.050,0.00150,TRUE,TRUE,'ACTIVE'),

('WH01','SITE01','ITEM014',
 'Energy Drink',
 'Energy drink can',
 'EA',0.400,0.00060,TRUE,TRUE,'ACTIVE'),

('WH01','SITE01','ITEM015',
 'Safety Gloves',
 'Industrial safety gloves',
 'PAIR',0.100,0.00030,FALSE,FALSE,'ACTIVE');


-- ============================================================
-- 5. CUSTOMERS
-- ============================================================

INSERT INTO customer_details (
    cu_warehouse_id,
    cu_site_id,
    cu_customer_number,
    cu_customer_name,
    cu_address_line1,
    cu_city,
    cu_state,
    cu_country,
    cu_zip,
    cu_phone,
    cu_email,
    cu_customer_status
)
VALUES

('WH01','SITE01','CUST001',
 'ABC Electronics LLC',
 'Business Bay',
 'Dubai','Dubai','UAE','00000',
 '+971500000101',
 'orders@abcelectronics.local',
 'ACTIVE'),

('WH01','SITE01','CUST002',
 'Dubai Office Supplies',
 'Al Quoz Industrial Area',
 'Dubai','Dubai','UAE','00000',
 '+971500000102',
 'orders@dubaioffice.local',
 'ACTIVE'),

('WH01','SITE01','CUST003',
 'Gulf Retail Trading',
 'Jebel Ali',
 'Dubai','Dubai','UAE','00000',
 '+971500000103',
 'orders@gulfretail.local',
 'ACTIVE'),

('WH01','SITE01','CUST004',
 'Tech World FZCO',
 'Dubai Silicon Oasis',
 'Dubai','Dubai','UAE','00000',
 '+971500000104',
 'orders@techworld.local',
 'ACTIVE');


-- ============================================================
-- 6. GOODS RECEIPTS
--
-- GR001 = normal receipt
-- GR002 = quantity discrepancy
-- GR003 = damaged goods
-- ============================================================

INSERT INTO goods_receipt_details (
    gr_warehouse_id,
    gr_site_id,
    gr_goods_receipt_number,
    gr_goods_receipt_position,
    gr_goods_receipt_item,
    gr_goods_receipt_quantity,
    gr_quantity_unit,
    gr_quality_code,
    gr_goods_receipt_status,
    gr_goods_receipt_date,
    gr_goods_receipt_time
)
VALUES

-- Normal receipt
('WH01','SITE01','GR001',1,'ITEM001',100,'EA',
 'GOOD','COMPLETED','2026-08-18','09:15:00'),

('WH01','SITE01','GR001',2,'ITEM002',80,'EA',
 'GOOD','COMPLETED','2026-08-18','09:15:00'),

('WH01','SITE01','GR001',3,'ITEM005',200,'EA',
 'GOOD','COMPLETED','2026-08-18','09:15:00'),

-- Quantity discrepancy:
-- Expected quantity was 150 but physically received 140.
-- Stored quantity reflects corrected physical quantity.
('WH01','SITE01','GR002',1,'ITEM003',140,'EA',
 'QTY_MISMATCH','COMPLETED','2026-08-18','11:30:00'),

-- Damaged goods:
-- 100 received, 10 damaged, 90 accepted.
('WH01','SITE01','GR003',1,'ITEM007',90,'EA',
 'DAMAGED','COMPLETED','2026-08-18','14:20:00');


-- ============================================================
-- 7. INVENTORY
--
-- Physical quantities deliberately contain several scenarios.
-- ============================================================

INSERT INTO inventory_details (
    iv_warehouse_id,
    iv_site_id,
    iv_item_id,
    iv_location_id,
    iv_aisle_number,
    iv_rack_number,
    iv_bin_number_horizontal,
    iv_bin_number_vertical,
    iv_load_unit_id,
    iv_physical_quantity,
    iv_quantity_unit,
    iv_allocated_quantity,
    iv_available_quantity,
    iv_blocked_quantity,
    iv_block_reason,
    iv_batch_number,
    iv_best_before_date,
    iv_received_at
)
VALUES

-- ==========================================================
-- Normal stock
-- ==========================================================

('WH01','SITE01','ITEM001',
 'BULK01','A01','R01','B01','01',
 'HU100001',
 100,'EA',20,80,0,NULL,NULL,NULL,
 '2026-08-18 09:30:00'),

('WH01','SITE01','ITEM002',
 'BULK01','A01','R01','B02','01',
 'HU100002',
 80,'EA',30,50,0,NULL,NULL,NULL,
 '2026-08-18 09:35:00'),

('WH01','SITE01','ITEM003',
 'BULK01','A01','R01','B03','01',
 'HU100003',
 140,'EA',0,140,0,NULL,NULL,NULL,
 '2026-08-18 11:45:00'),

('WH01','SITE01','ITEM004',
 'BULK01','A01','R02','B01','01',
 'HU100004',
 60,'EA',0,60,0,NULL,NULL,NULL,
 '2026-08-17 10:00:00'),

('WH01','SITE01','ITEM005',
 'BULK01','A01','R02','B02','01',
 'HU100005',
 200,'EA',50,150,0,NULL,NULL,NULL,
 '2026-08-18 09:40:00'),

('WH01','SITE01','ITEM006',
 'BULK01','A01','R02','B03','01',
 'HU100006',
 25,'EA',5,20,0,NULL,NULL,NULL,
 '2026-08-16 15:00:00'),


-- ==========================================================
-- Batch controlled printer toner
-- ==========================================================

('WH01','SITE01','ITEM007',
 'BULK01','A02','R01','B01','01',
 'HU100007',
 90,'EA',20,70,0,NULL,
 'TONER-B2026-01',NULL,
 '2026-08-18 14:40:00'),


-- ==========================================================
-- BBD + Batch controlled sanitizer
-- ==========================================================

('WH01','SITE01','ITEM008',
 'BULK01','A02','R01','B02','01',
 'HU100008',
 50,'EA',0,50,0,NULL,
 'SAN-B001','2027-06-30',
 '2026-08-17 09:00:00'),


-- ==========================================================
-- BBD item
-- ==========================================================

('WH01','SITE01','ITEM009',
 'PICK01','P01','R01','B01','01',
 'HU100009',
 40,'EA',10,30,0,NULL,
 NULL,'2027-01-31',
 '2026-08-15 12:00:00'),


-- ==========================================================
-- Packing materials
-- ==========================================================

('WH01','SITE01','ITEM010',
 'PICK01','P01','R01','B02','01',
 'HU100010',
 300,'EA',50,250,0,NULL,NULL,NULL,
 '2026-08-10 10:00:00'),

('WH01','SITE01','ITEM011',
 'BULK01','A02','R01','B02','01',
 'HU100011',
 500,'EA',100,400,0,NULL,NULL,NULL,
 '2026-08-10 10:00:00'),

('WH01','SITE01','ITEM012',
 'BULK01','A02','R01','B03','01',
 'HU100012',
 200,'EA',0,200,0,NULL,NULL,NULL,
 '2026-08-10 10:00:00'),


-- ==========================================================
-- Coffee - batch/BBD controlled
-- ==========================================================

('WH01','SITE01','ITEM013',
 'BULK01','A02','R01','B04','01',
 'HU100013',
 75,'EA',25,50,0,NULL,
 'COFFEE-B100','2026-12-31',
 '2026-08-12 08:00:00'),


-- ==========================================================
-- Energy drink - deliberately blocked stock
-- ==========================================================

('WH01','SITE01','ITEM014',
 'BULK01','A01','R02','B04','01',
 'HU100014',
 100,'EA',20,30,50,
 'QUALITY_HOLD',
 'ENERGY-B200','2026-11-30',
 '2026-08-13 09:00:00'),


-- ==========================================================
-- Safety gloves
-- ==========================================================

('WH01','SITE01','ITEM015',
 'BULK01','A01','R01','B04','01',
 'HU100015',
 200,'PAIR',0,200,0,NULL,NULL,NULL,
 '2026-08-14 09:00:00');


-- ============================================================
-- 8. ORDERS
-- ============================================================

INSERT INTO order_header_details (
    oh_warehouse_id,
    oh_site_id,
    oh_order_number,
    oh_order_date,
    oh_order_time,
    oh_order_status,
    oh_allocation_status,
    oh_picking_status,
    oh_packing_status,
    oh_loading_status,
    oh_customer_number,
    oh_customer_name,
    oh_address_line1,
    oh_city,
    oh_state,
    oh_country,
    oh_zip,
    oh_phone,
    oh_email,
    oh_delivery_date,
    oh_delivery_time
)
VALUES

-- Completed/normal order
('WH01','SITE01','ORD10001',
 '2026-08-19','08:30:00',
 'RELEASED',
 'ALLOCATED',
 'IN_PROGRESS',
 'NOT_STARTED',
 'NOT_STARTED',
 'CUST001',
 'ABC Electronics LLC',
 'Business Bay',
 'Dubai','Dubai','UAE','00000',
 '+971500000101',
 'orders@abcelectronics.local',
 '2026-08-20','10:00:00'),

-- Order with allocation shortage
('WH01','SITE01','ORD10002',
 '2026-08-19','09:15:00',
 'ALLOCATED',
 'PARTIAL',
 'NOT_STARTED',
 'NOT_STARTED',
 'NOT_STARTED',
 'CUST002',
 'Dubai Office Supplies',
 'Al Quoz Industrial Area',
 'Dubai','Dubai','UAE','00000',
 '+971500000102',
 'orders@dubaioffice.local',
 '2026-08-20','12:00:00'),

-- Normal order ready for allocation
('WH01','SITE01','ORD10003',
 '2026-08-19','10:20:00',
 'CREATED',
 'NOT_ALLOCATED',
 'NOT_STARTED',
 'NOT_STARTED',
 'NOT_STARTED',
 'CUST003',
 'Gulf Retail Trading',
 'Jebel Ali',
 'Dubai','Dubai','UAE','00000',
 '+971500000103',
 'orders@gulfretail.local',
 '2026-08-21','09:00:00'),

-- Order affected by blocked inventory
('WH01','SITE01','ORD10004',
 '2026-08-19','11:00:00',
 'ALLOCATED',
 'PARTIAL',
 'NOT_STARTED',
 'NOT_STARTED',
 'NOT_STARTED',
 'CUST004',
 'Tech World FZCO',
 'Dubai Silicon Oasis',
 'Dubai','Dubai','UAE','00000',
 '+971500000104',
 'orders@techworld.local',
 '2026-08-21','14:00:00');


-- ============================================================
-- 9. ORDER POSITIONS
-- ============================================================

INSERT INTO order_position_details (
    op_warehouse_id,
    op_site_id,
    op_order_number,
    op_order_position,
    op_order_item,
    op_order_quantity,
    op_quantity_unit,
    op_allocated_quantity,
    op_picked_quantity
)
VALUES

-- ORD10001
('WH01','SITE01','ORD10001',10,'ITEM001',
 20,'EA',20,0),

('WH01','SITE01','ORD10001',20,'ITEM002',
 30,'EA',30,0),

('WH01','SITE01','ORD10001',30,'ITEM005',
 50,'EA',50,0),


-- ORD10002
-- Requested 100, only 50 available/allocated
('WH01','SITE01','ORD10002',10,'ITEM002',
 100,'EA',50,0),

('WH01','SITE01','ORD10002',20,'ITEM003',
 50,'EA',50,0),


-- ORD10003
('WH01','SITE01','ORD10003',10,'ITEM004',
 10,'EA',0,0),

('WH01','SITE01','ORD10003',20,'ITEM015',
 30,'PAIR',0,0),


-- ORD10004
-- ITEM014 has 50 physical but 50 blocked and only 30 available
('WH01','SITE01','ORD10004',10,'ITEM014',
 60,'EA',30,0),

('WH01','SITE01','ORD10004',20,'ITEM007',
 10,'EA',10,0);


-- ============================================================
-- 10. MOVEMENTS
--
-- These represent transport/movement records.
-- ============================================================

INSERT INTO movement_details (
    mo_warehouse_id,
    mo_site_id,
    mo_movement_id,
    mo_movement_type,
    mo_movement_status,
    mo_movement_item,
    mo_movement_quantity,
    mo_movement_quantity_unit,

    mo_movement_from_entry_area,
    mo_movement_from_location_id,
    mo_movement_from_aisle_number,
    mo_movement_from_rack_number,
    mo_movement_from_bin_hor,
    mo_movement_from_bin_ver,

    mo_movement_to_location_id,
    mo_movement_to_aisle_number,
    mo_movement_to_rack_number,
    mo_movement_to_bin_hor,
    mo_movement_to_bin_ver,

    mo_movement_to_exit_area,

    mo_movement_date,
    mo_movement_time
)
VALUES

-- ==========================================================
-- INBOUND PUTAWAY
-- ==========================================================

('WH01','SITE01','MOV00001',
 'INBOUND','COMPLETED',
 'ITEM001',100,'EA',
 'GR01',
 NULL,NULL,NULL,NULL,NULL,
 'BULK01','A01','R01','B01','01',
 NULL,
 '2026-08-18','09:45:00'),

('WH01','SITE01','MOV00002',
 'INBOUND','COMPLETED',
 'ITEM002',80,'EA',
 'GR01',
 NULL,NULL,NULL,NULL,NULL,
 'BULK01','A01','R01','B02','01',
 NULL,
 '2026-08-18','09:50:00'),

('WH01','SITE01','MOV00003',
 'INBOUND','COMPLETED',
 'ITEM005',200,'EA',
 'GR01',
 NULL,NULL,NULL,NULL,NULL,
 'BULK01','A01','R02','B02','01',
 NULL,
 '2026-08-18','09:55:00'),

-- GR002 corrected quantity = 140
('WH01','SITE01','MOV00004',
 'INBOUND','COMPLETED',
 'ITEM003',140,'EA',
 'GR01',
 NULL,NULL,NULL,NULL,NULL,
 'BULK01','A01','R01','B03','01',
 NULL,
 '2026-08-18','12:00:00'),

-- Damaged GR accepted quantity = 90
('WH01','SITE01','MOV00005',
 'INBOUND','COMPLETED',
 'ITEM007',90,'EA',
 'GR01',
 NULL,NULL,NULL,NULL,NULL,
 'BULK01','A02','R01','B01','01',
 NULL,
 '2026-08-18','14:50:00'),


-- ==========================================================
-- OUTBOUND PICKING
-- Bin -> Exit staging
-- ==========================================================

('WH01','SITE01','MOV00006',
 'OUTBOUND','OPEN',
 'ITEM001',20,'EA',
 NULL,
 'BULK01','A01','R01','B01','01',
 'EXIT01',NULL,NULL,NULL,NULL,
 'EXIT01',
 '2026-08-19','09:00:00'),

('WH01','SITE01','MOV00007',
 'OUTBOUND','OPEN',
 'ITEM002',30,'EA',
 NULL,
 'BULK01','A01','R01','B02','01',
 'EXIT01',NULL,NULL,NULL,NULL,
 'EXIT01',
 '2026-08-19','09:05:00'),

('WH01','SITE01','MOV00008',
 'OUTBOUND','OPEN',
 'ITEM005',50,'EA',
 NULL,
 'BULK01','A01','R02','B02','01',
 'EXIT01',NULL,NULL,NULL,NULL,
 'EXIT01',
 '2026-08-19','09:10:00'),


-- ==========================================================
-- INTERNAL RELOCATION
-- ==========================================================

('WH01','SITE01','MOV00009',
 'INTERNAL','COMPLETED',
 'ITEM004',10,'EA',
 NULL,
 'BULK01','A01','R02','B01','01',
 'PICK01','P01','R01','B03','01',
 NULL,
 '2026-08-18','16:00:00'),


-- ==========================================================
-- PICKING MOVEMENT for ORD10002
-- ==========================================================

('WH01','SITE01','MOV00010',
 'OUTBOUND','OPEN',
 'ITEM002',50,'EA',
 NULL,
 'BULK01','A01','R01','B02','01',
 'EXIT01',NULL,NULL,NULL,NULL,
 'EXIT01',
 '2026-08-19','10:00:00');


-- ============================================================
-- 11. VALIDATION QUERY
-- ============================================================

SELECT
    iv_warehouse_id,
    iv_site_id,
    iv_item_id,
    iv_location_id,
    iv_physical_quantity,
    iv_allocated_quantity,
    iv_blocked_quantity,
    iv_available_quantity
FROM inventory_details
ORDER BY iv_item_id;


COMMIT;

-- ============================================================
-- END OF 02_seed_wms_data.sql
-- ============================================================