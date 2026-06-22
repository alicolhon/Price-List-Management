export interface CalculationResult {
  material_10: string;
  rrp_future_rounded: number | null;
  rrp_change_pct: number | null;
  ipp_current_rrp_based: number | null;
  ipp_current_np_based: number | null;
  ipp_final_current: number | null;
  ipp_future_rrp_based: number | null;
  ipp_future_np_based: number | null;
  ipp_final_future: number | null;
  ipp_change_pct: number | null;
  npp_current_de21: number | null;
  npp_future_de21: number | null;
  npp_change_pct: number | null;
  np_platinum_lc_future: number | null;
  np_gold_lc: number | null;
  np_silver_lc: number | null;
  np_bronze_lc: number | null;
  np_gold_lc_future: number | null;
  np_silver_lc_future: number | null;
  np_bronze_lc_future: number | null;
  deviation_intercars: number | null;
  deviation_autonet: number | null;
  deviation_truck: number | null;
  deviation_lkq: number | null;
  current_margin: number | null;
  new_margin: number | null;
  current_violation: 'OK' | 'MIN' | 'MAX' | 'ROTTEN_APPLE';
  future_violation: 'OK' | 'MIN' | 'MAX' | 'ROTTEN_APPLE';
  flag_ipp_change_above_10: boolean;
  flag_ipp_future_above_rrp: boolean;
  flag_minderrabatt: boolean;
  flag_min_npp_violation: boolean;
  flag_rotten_apple: boolean;
  ipp_volume_current: number | null;
  ipp_volume_future: number | null;
  rrp_at_alignment: number | null;
  rrp_ch_alignment: number | null;
  price_proposal_min_rrp: number | null;
  price_proposal_max_rrp: number | null;
}

export interface Product {
  id: number;
  material_10: string;
  material_13: string | null;
  description_en: string | null;
  description_de: string | null;
  sales_org: string | null;
  status: string | null;
  pg1_current: string | null;
  pg2_current: string | null;
  pg3_current: string | null;
  pg1_description: string | null;
  pg2_description: string | null;
  pg3_description: string | null;
  pg1_2026: string | null;
  pg2_2026: string | null;
  pg3_2026: string | null;
  pg1_description_2026_en: string | null;
  pg2_description_2026_en: string | null;
  pg3_description_2026_en: string | null;
  pg_structure_change_2026: string | null;
  discount_group_current: string | null;
  discount_group_future: string | null;
  max_basic_discount_current: number | null;
  max_add_discount_current: number | null;
  future_basic_discount: number | null;
  future_add_discount: number | null;
  bonus_sde: number | null;
  predecessor: string | null;
  successor: string | null;
  fg_pkw: boolean | null;
  fg_nkw: boolean | null;
  fg_krad: boolean | null;
  fg_motor: boolean | null;
  abc_sales: string | null;
  abc_qty: string | null;
  abc_vehicle_population: string | null;
  qty_12m: number | null;
  ipp_12m: number | null;
  qty_ly_total: number | null;
  ipp_ly_total: number | null;
  fepaa: number | null;
  hinweise_sms41: string | null;
  eznrart: string | null;
  // Historical RRP
  rrp_01_2023: number | null;
  rrp_04_2023: number | null;
  rrp_07_2023: number | null;
  rrp_10_2023: number | null;
  rrp_01_2024: number | null;
  rrp_04_2024: number | null;
  rrp_07_2024: number | null;
  rrp_10_2024: number | null;
  rrp_01_2025: number | null;
  rrp_04_2025: number | null;
  rrp_07_2025: number | null;
  rrp_10_2025: number | null;
  rrp_current_01_2026: number | null;
  // Editable inputs
  rrp_future_04_2026: number | null;
  np_platinum_lc: number | null;
  np_platinum_manual_override: boolean | null;
  reason_manual_override: string | null;
  minimum_npp_eur: number | null;
  maximum_npp_eur: number | null;
  exception_flag: string | null;
  ps_action: string | null;
  comment_rrp: string | null;
  comment_np: string | null;
  // Benchmarks
  npp_pl_intercars: number | null;
  npp_autonet: number | null;
  npp_truck: number | null;
  npp_lkq: number | null;
  zk76_truck: string | null;
  bonus_lkq: number | null;
  // Comments
  comment_04_2023: string | null;
  comment_07_2023: string | null;
  comment_04_2024: string | null;
  comment_07_2024: string | null;
  comment_01_2025: string | null;
  comment_04_2025: string | null;
  comment_07_2025: string | null;
  comment_10_2025: string | null;
  comment_01_2026: string | null;
  comment_04_2026: string | null;
  // Volume adjusted
  ipp_volume_current_adj: number | null;
  ipp_volume_future_adj: number | null;
  rrp_volume_current_adj: number | null;
  rrp_volume_future_adj: number | null;
  calc: CalculationResult | null;
}

export interface ProductListResponse {
  total: number;
  page: number;
  page_size: number;
  items: Product[];
}

export interface SummaryStats {
  total_products: number;
  active_products: number;
  total_violations: number;
  rotten_apples: number;
  min_violations: number;
  max_violations: number;
  total_ipp_volume_current: number;
  total_ipp_volume_future: number;
  weighted_rrp_change_pct: number | null;
  weighted_ipp_change_pct: number | null;
}

export interface ProductUpdate {
  rrp_future_04_2026?: number | null;
  np_platinum_lc?: number | null;
  np_platinum_manual_override?: boolean | null;
  reason_manual_override?: string | null;
  minimum_npp_eur?: number | null;
  maximum_npp_eur?: number | null;
  exception_flag?: string | null;
  ps_action?: string | null;
  comment_rrp?: string | null;
  comment_np?: string | null;
  comment_04_2026?: string | null;
  hinweise_sms41?: string | null;
}

export interface Filters {
  search: string;
  pg1: string;
  pg2: string;
  status: string;
  abc_sales: string;
  violation: string;
  discount_group: string;
}
