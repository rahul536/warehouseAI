-- ============================================================
-- WarehouseAI - WMS Database Master Schema
-- File: 01_warehouse_master.sql
-- PostgreSQL 18+
-- ============================================================

BEGIN;

-- ============================================================
-- 1. WAREHOUSE / SITE
-- ============================================================

CREATE TABLE warehouse_site_details (
    ws_warehouse_id       VARCHAR(20)  NOT NULL,
    ws_site_id            VARCHAR(20)  NOT NULL,
    ws_site_name          VARCHAR(100) NOT NULL,
    ws_description        VARCHAR(255),
    ws_status             VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE',

    ws_address_line1      VARCHAR(255),
    ws_address_line2      VARCHAR(255),
    ws_city               VARCHAR(100),
    ws_state              VARCHAR(100),
    ws_country            VARCHAR(100),
    ws_zip                VARCHAR(20),
    ws_phone              VARCHAR(50),
    ws_fax                VARCHAR(50),
    ws_email              VARCHAR(150),

    ws_created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ws_updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_warehouse_site_details
        PRIMARY KEY (ws_warehouse_id, ws_site_id),

    CONSTRAINT chk_ws_status
        CHECK (ws_status IN ('ACTIVE', 'INACTIVE'))
);


-- ============================================================
-- 2. STORAGE LOCATION
-- Logical storage location within warehouse/site
-- ============================================================

CREATE TABLE storage_location_details (
    sl_warehouse_id                VARCHAR(20) NOT NULL,
    sl_site_id                     VARCHAR(20) NOT NULL,
    sl_zone                        VARCHAR(50),
    sl_location_id                 VARCHAR(50) NOT NULL,
    sl_status                      VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    sl_mixed_hu_allowed            BOOLEAN NOT NULL DEFAULT FALSE,
    sl_inventory_addition_allowed  BOOLEAN NOT NULL DEFAULT TRUE,
    sl_capacity_check_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    sl_allocation_enabled           BOOLEAN NOT NULL DEFAULT TRUE,
    sl_replenishment_enabled        BOOLEAN NOT NULL DEFAULT FALSE,

    sl_created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sl_updated_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_storage_location_details
        PRIMARY KEY (
            sl_warehouse_id,
            sl_site_id,
            sl_location_id
        ),

    CONSTRAINT fk_sl_warehouse_site
        FOREIGN KEY (
            sl_warehouse_id,
            sl_site_id
        )
        REFERENCES warehouse_site_details (
            ws_warehouse_id,
            ws_site_id
        ),

    CONSTRAINT chk_sl_status
        CHECK (sl_status IN ('ACTIVE', 'INACTIVE'))
);


-- ============================================================
-- 3. STORAGE BIN
-- Physical aisle/rack/bin structure
-- ============================================================

CREATE TABLE storage_bin_details (
    sb_warehouse_id              VARCHAR(20) NOT NULL,
    sb_site_id                   VARCHAR(20) NOT NULL,
    sb_zone                      VARCHAR(50),
    sb_location_id               VARCHAR(50) NOT NULL,

    sb_aisle_number              VARCHAR(30) NOT NULL,
    sb_rack_number               VARCHAR(30) NOT NULL,
    sb_bin_number_horizontal     VARCHAR(30) NOT NULL,
    sb_bin_number_vertical       VARCHAR(30) NOT NULL,

    sb_bin_status                VARCHAR(20) NOT NULL DEFAULT 'EMPTY',

    sb_created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sb_updated_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_storage_bin_details
        PRIMARY KEY (
            sb_warehouse_id,
            sb_site_id,
            sb_location_id,
            sb_aisle_number,
            sb_rack_number,
            sb_bin_number_horizontal,
            sb_bin_number_vertical
        ),

    CONSTRAINT fk_sb_storage_location
        FOREIGN KEY (
            sb_warehouse_id,
            sb_site_id,
            sb_location_id
        )
        REFERENCES storage_location_details (
            sl_warehouse_id,
            sl_site_id,
            sl_location_id
        ),

    CONSTRAINT chk_sb_status
        CHECK (
            sb_bin_status IN (
                'EMPTY',
                'OCCUPIED',
                'BLOCKED',
                'INACTIVE'
            )
        )
);


-- ============================================================
-- 4. ITEM
-- ============================================================

CREATE TABLE item_details (
    it_warehouse_id       VARCHAR(20) NOT NULL,
    it_site_id            VARCHAR(20) NOT NULL,
    it_item_id            VARCHAR(50) NOT NULL,

    it_item_name          VARCHAR(150) NOT NULL,
    it_description        VARCHAR(255),
    it_uom                VARCHAR(20) NOT NULL,

    it_unit_weight_kg     NUMERIC(18,6),
    it_unit_volume_m3     NUMERIC(18,9),

    it_bbd_mandatory      BOOLEAN NOT NULL DEFAULT FALSE,
    it_batch_mandatory    BOOLEAN NOT NULL DEFAULT FALSE,

    it_status             VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    it_created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    it_updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_item_details
        PRIMARY KEY (
            it_warehouse_id,
            it_site_id,
            it_item_id
        ),

    CONSTRAINT fk_it_warehouse_site
        FOREIGN KEY (
            it_warehouse_id,
            it_site_id
        )
        REFERENCES warehouse_site_details (
            ws_warehouse_id,
            ws_site_id
        ),

    CONSTRAINT chk_it_status
        CHECK (it_status IN ('ACTIVE', 'INACTIVE')),

    CONSTRAINT chk_it_weight
        CHECK (
            it_unit_weight_kg IS NULL
            OR it_unit_weight_kg >= 0
        ),

    CONSTRAINT chk_it_volume
        CHECK (
            it_unit_volume_m3 IS NULL
            OR it_unit_volume_m3 >= 0
        )
);


-- ============================================================
-- 5. INVENTORY
--
-- Available quantity is calculated and stored:
--
-- physical - allocated - blocked = available
--
-- Batch/BBD are optional.
-- ============================================================

CREATE TABLE inventory_details (
    iv_warehouse_id          VARCHAR(20) NOT NULL,
    iv_site_id               VARCHAR(20) NOT NULL,
    iv_item_id               VARCHAR(50) NOT NULL,

    iv_location_id           VARCHAR(50) NOT NULL,
    iv_aisle_number          VARCHAR(30),
    iv_rack_number           VARCHAR(30),
    iv_bin_number_horizontal VARCHAR(30),
    iv_bin_number_vertical   VARCHAR(30),

    iv_load_unit_id          VARCHAR(50),

    iv_physical_quantity     NUMERIC(18,3) NOT NULL DEFAULT 0,
    iv_quantity_unit         VARCHAR(20) NOT NULL,

    iv_allocated_quantity    NUMERIC(18,3) NOT NULL DEFAULT 0,
    iv_available_quantity    NUMERIC(18,3) NOT NULL DEFAULT 0,
    iv_blocked_quantity      NUMERIC(18,3) NOT NULL DEFAULT 0,

    iv_block_reason          VARCHAR(255),

    iv_batch_number          VARCHAR(100),
    iv_best_before_date      DATE,

    iv_received_at           TIMESTAMP,

    iv_created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    iv_updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_iv_item
        FOREIGN KEY (
            iv_warehouse_id,
            iv_site_id,
            iv_item_id
        )
        REFERENCES item_details (
            it_warehouse_id,
            it_site_id,
            it_item_id
        ),

    CONSTRAINT fk_iv_storage_location
        FOREIGN KEY (
            iv_warehouse_id,
            iv_site_id,
            iv_location_id
        )
        REFERENCES storage_location_details (
            sl_warehouse_id,
            sl_site_id,
            sl_location_id
        ),

    CONSTRAINT chk_iv_quantities
        CHECK (
            iv_physical_quantity >= 0
            AND iv_allocated_quantity >= 0
            AND iv_blocked_quantity >= 0
            AND iv_available_quantity >= 0
        ),

    CONSTRAINT chk_iv_available_quantity
        CHECK (
            iv_available_quantity =
            iv_physical_quantity
            - iv_allocated_quantity
            - iv_blocked_quantity
        )
);

-- Inventory identity including nullable batch/BBD/HU.
-- NULLS NOT DISTINCT makes NULL values participate in uniqueness.
CREATE UNIQUE INDEX uq_inventory_identity
ON inventory_details (
    iv_warehouse_id,
    iv_site_id,
    iv_item_id,
    iv_location_id,
    iv_aisle_number,
    iv_rack_number,
    iv_bin_number_horizontal,
    iv_bin_number_vertical,
    iv_load_unit_id,
    iv_batch_number,
    iv_best_before_date
) NULLS NOT DISTINCT;


-- ============================================================
-- 6. CUSTOMER
-- ============================================================

CREATE TABLE customer_details (
    cu_warehouse_id       VARCHAR(20) NOT NULL,
    cu_site_id            VARCHAR(20) NOT NULL,
    cu_customer_number    VARCHAR(50) NOT NULL,

    cu_customer_name      VARCHAR(150) NOT NULL,

    cu_address_line1      VARCHAR(255),
    cu_address_line2      VARCHAR(255),
    cu_city               VARCHAR(100),
    cu_state              VARCHAR(100),
    cu_country            VARCHAR(100),
    cu_zip                VARCHAR(20),

    cu_phone              VARCHAR(50),
    cu_fax                VARCHAR(50),
    cu_email              VARCHAR(150),

    cu_customer_status    VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    cu_created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cu_updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_customer_details
        PRIMARY KEY (
            cu_warehouse_id,
            cu_site_id,
            cu_customer_number
        ),

    CONSTRAINT fk_cu_warehouse_site
        FOREIGN KEY (
            cu_warehouse_id,
            cu_site_id
        )
        REFERENCES warehouse_site_details (
            ws_warehouse_id,
            ws_site_id
        ),

    CONSTRAINT chk_cu_status
        CHECK (
            cu_customer_status IN ('ACTIVE', 'INACTIVE')
        )
);


-- ============================================================
-- 7. ORDER HEADER
-- ============================================================

CREATE TABLE order_header_details (
    oh_warehouse_id       VARCHAR(20) NOT NULL,
    oh_site_id            VARCHAR(20) NOT NULL,
    oh_order_number       VARCHAR(50) NOT NULL,

    oh_order_date         DATE NOT NULL,
    oh_order_time         TIME NOT NULL,

    oh_order_status       VARCHAR(30) NOT NULL DEFAULT 'CREATED',
    oh_allocation_status  VARCHAR(30) NOT NULL DEFAULT 'NOT_ALLOCATED',
    oh_picking_status     VARCHAR(30) NOT NULL DEFAULT 'NOT_STARTED',
    oh_packing_status     VARCHAR(30) NOT NULL DEFAULT 'NOT_STARTED',
    oh_loading_status     VARCHAR(30) NOT NULL DEFAULT 'NOT_STARTED',

    oh_customer_number    VARCHAR(50) NOT NULL,
    oh_customer_name      VARCHAR(150),

    oh_address_line1      VARCHAR(255),
    oh_address_line2      VARCHAR(255),
    oh_city               VARCHAR(100),
    oh_state              VARCHAR(100),
    oh_country            VARCHAR(100),
    oh_zip                VARCHAR(20),

    oh_phone              VARCHAR(50),
    oh_fax                VARCHAR(50),
    oh_email              VARCHAR(150),

    oh_delivery_date      DATE,
    oh_delivery_time      TIME,

    oh_created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    oh_updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_order_header_details
        PRIMARY KEY (
            oh_warehouse_id,
            oh_site_id,
            oh_order_number
        ),

    CONSTRAINT fk_oh_warehouse_site
        FOREIGN KEY (
            oh_warehouse_id,
            oh_site_id
        )
        REFERENCES warehouse_site_details (
            ws_warehouse_id,
            ws_site_id
        ),

    CONSTRAINT fk_oh_customer
        FOREIGN KEY (
            oh_warehouse_id,
            oh_site_id,
            oh_customer_number
        )
        REFERENCES customer_details (
            cu_warehouse_id,
            cu_site_id,
            cu_customer_number
        )
);


-- ============================================================
-- 8. ORDER POSITION
-- ============================================================

CREATE TABLE order_position_details (
    op_warehouse_id        VARCHAR(20) NOT NULL,
    op_site_id             VARCHAR(20) NOT NULL,

    op_order_number        VARCHAR(50) NOT NULL,
    op_order_position      INTEGER NOT NULL,

    op_order_item          VARCHAR(50) NOT NULL,
    op_order_quantity      NUMERIC(18,3) NOT NULL,
    op_quantity_unit       VARCHAR(20) NOT NULL,

    op_allocated_quantity  NUMERIC(18,3) NOT NULL DEFAULT 0,
    op_picked_quantity     NUMERIC(18,3) NOT NULL DEFAULT 0,

    op_created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    op_updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_order_position_details
        PRIMARY KEY (
            op_warehouse_id,
            op_site_id,
            op_order_number,
            op_order_position
        ),

    CONSTRAINT fk_op_order
        FOREIGN KEY (
            op_warehouse_id,
            op_site_id,
            op_order_number
        )
        REFERENCES order_header_details (
            oh_warehouse_id,
            oh_site_id,
            oh_order_number
        ),

    CONSTRAINT fk_op_item
        FOREIGN KEY (
            op_warehouse_id,
            op_site_id,
            op_order_item
        )
        REFERENCES item_details (
            it_warehouse_id,
            it_site_id,
            it_item_id
        ),

    CONSTRAINT chk_op_quantities
        CHECK (
            op_order_quantity >= 0
            AND op_allocated_quantity >= 0
            AND op_picked_quantity >= 0
            AND op_allocated_quantity <= op_order_quantity
            AND op_picked_quantity <= op_allocated_quantity
        )
);


-- ============================================================
-- 9. GOODS RECEIPT
-- ============================================================

CREATE TABLE goods_receipt_details (
    gr_warehouse_id           VARCHAR(20) NOT NULL,
    gr_site_id                VARCHAR(20) NOT NULL,

    gr_goods_receipt_number   VARCHAR(50) NOT NULL,
    gr_goods_receipt_position INTEGER NOT NULL,

    gr_goods_receipt_item     VARCHAR(50) NOT NULL,
    gr_goods_receipt_quantity NUMERIC(18,3) NOT NULL,
    gr_quantity_unit          VARCHAR(20) NOT NULL,

    gr_quality_code           VARCHAR(30),
    gr_goods_receipt_status   VARCHAR(30) NOT NULL DEFAULT 'OPEN',

    gr_goods_receipt_date     DATE NOT NULL,
    gr_goods_receipt_time     TIME NOT NULL,

    gr_created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gr_updated_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_goods_receipt_details
        PRIMARY KEY (
            gr_warehouse_id,
            gr_site_id,
            gr_goods_receipt_number,
            gr_goods_receipt_position
        ),

    CONSTRAINT fk_gr_warehouse_site
        FOREIGN KEY (
            gr_warehouse_id,
            gr_site_id
        )
        REFERENCES warehouse_site_details (
            ws_warehouse_id,
            ws_site_id
        ),

    CONSTRAINT fk_gr_item
        FOREIGN KEY (
            gr_warehouse_id,
            gr_site_id,
            gr_goods_receipt_item
        )
        REFERENCES item_details (
            it_warehouse_id,
            it_site_id,
            it_item_id
        ),

    CONSTRAINT chk_gr_quantity
        CHECK (
            gr_goods_receipt_quantity >= 0
        )
);


-- ============================================================
-- 10. MOVEMENT
--
-- One movement record represents one movement/transport.
--
-- INBOUND:
--     Entry staging -> Bin
--
-- OUTBOUND:
--     Bin -> Picking/Exit staging
--     Picking/Exit staging -> Packing
--     Packing -> Final loading area
--
-- INTERNAL:
--     Bin -> Bin
-- ============================================================

CREATE TABLE movement_details (
    mo_warehouse_id              VARCHAR(20) NOT NULL,
    mo_site_id                   VARCHAR(20) NOT NULL,

    mo_movement_id               VARCHAR(50) NOT NULL,
    mo_movement_type             VARCHAR(30) NOT NULL,
    mo_movement_status           VARCHAR(30) NOT NULL DEFAULT 'OPEN',

    mo_movement_item             VARCHAR(50) NOT NULL,
    mo_movement_quantity         NUMERIC(18,3) NOT NULL,
    mo_movement_quantity_unit    VARCHAR(20) NOT NULL,

    mo_movement_from_entry_area  VARCHAR(50),

    mo_movement_from_location_id VARCHAR(50),
    mo_movement_from_aisle_number VARCHAR(30),
    mo_movement_from_rack_number  VARCHAR(30),
    mo_movement_from_bin_hor       VARCHAR(30),
    mo_movement_from_bin_ver       VARCHAR(30),

    mo_movement_to_location_id   VARCHAR(50),
    mo_movement_to_aisle_number  VARCHAR(30),
    mo_movement_to_rack_number   VARCHAR(30),
    mo_movement_to_bin_hor       VARCHAR(30),
    mo_movement_to_bin_ver       VARCHAR(30),

    mo_movement_to_exit_area     VARCHAR(50),

    mo_movement_date             DATE NOT NULL,
    mo_movement_time             TIME NOT NULL,

    mo_created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mo_updated_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_movement_details
        PRIMARY KEY (
            mo_warehouse_id,
            mo_site_id,
            mo_movement_id
        ),

    CONSTRAINT fk_mo_warehouse_site
        FOREIGN KEY (
            mo_warehouse_id,
            mo_site_id
        )
        REFERENCES warehouse_site_details (
            ws_warehouse_id,
            ws_site_id
        ),

    CONSTRAINT fk_mo_item
        FOREIGN KEY (
            mo_warehouse_id,
            mo_site_id,
            mo_movement_item
        )
        REFERENCES item_details (
            it_warehouse_id,
            it_site_id,
            it_item_id
        ),

    CONSTRAINT fk_mo_from_location
        FOREIGN KEY (
            mo_warehouse_id,
            mo_site_id,
            mo_movement_from_location_id
        )
        REFERENCES storage_location_details (
            sl_warehouse_id,
            sl_site_id,
            sl_location_id
        ),

    CONSTRAINT fk_mo_to_location
        FOREIGN KEY (
            mo_warehouse_id,
            mo_site_id,
            mo_movement_to_location_id
        )
        REFERENCES storage_location_details (
            sl_warehouse_id,
            sl_site_id,
            sl_location_id
        ),

    CONSTRAINT chk_mo_quantity
        CHECK (
            mo_movement_quantity >= 0
        )
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_sl_warehouse_site_zone
    ON storage_location_details (
        sl_warehouse_id,
        sl_site_id,
        sl_zone
    );

CREATE INDEX idx_sb_location
    ON storage_bin_details (
        sb_warehouse_id,
        sb_site_id,
        sb_location_id
    );

CREATE INDEX idx_item_status
    ON item_details (
        it_warehouse_id,
        it_site_id,
        it_status
    );

CREATE INDEX idx_inventory_item_location
    ON inventory_details (
        iv_warehouse_id,
        iv_site_id,
        iv_item_id,
        iv_location_id
    );

CREATE INDEX idx_inventory_available
    ON inventory_details (
        iv_warehouse_id,
        iv_site_id,
        iv_item_id,
        iv_available_quantity
    );

CREATE INDEX idx_inventory_load_unit
    ON inventory_details (
        iv_warehouse_id,
        iv_site_id,
        iv_load_unit_id
    );

CREATE INDEX idx_inventory_batch
    ON inventory_details (
        iv_warehouse_id,
        iv_site_id,
        iv_item_id,
        iv_batch_number
    );

CREATE INDEX idx_order_header_status
    ON order_header_details (
        oh_warehouse_id,
        oh_site_id,
        oh_order_status
    );

CREATE INDEX idx_order_header_customer
    ON order_header_details (
        oh_warehouse_id,
        oh_site_id,
        oh_customer_number
    );

CREATE INDEX idx_order_position_item
    ON order_position_details (
        op_warehouse_id,
        op_site_id,
        op_order_item
    );

CREATE INDEX idx_gr_status
    ON goods_receipt_details (
        gr_warehouse_id,
        gr_site_id,
        gr_goods_receipt_status
    );

CREATE INDEX idx_movement_status
    ON movement_details (
        mo_warehouse_id,
        mo_site_id,
        mo_movement_status
    );

CREATE INDEX idx_movement_item
    ON movement_details (
        mo_warehouse_id,
        mo_site_id,
        mo_movement_item
    );


COMMIT;

-- ============================================================
-- END OF 01_warehouse_master.sql
-- ============================================================