export interface DocumentRecord {
  id: string
  title: string | null
  file_path: string
  type: string | null
  category: string | null
  linked_module: string | null
  owner_id: string | null
  customer_id: string | null
  uploaded_at: string | null
  checksum: string | null
  is_confidential: boolean
  file_size: number | null
  download_url: string | null
}

export interface DocumentListResponse {
  total: number
  page: number
  page_size: number
  documents: DocumentRecord[]
}

export interface DocumentUpdate {
  title?: string
  category?: string
  linked_module?: string
  is_confidential?: boolean
}
