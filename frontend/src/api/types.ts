export interface Source {
  provision_id: string;
  tag: 'R' | 'G' | null;
  text: string;
}

export interface QueryResponse {
  query: string;
  search_query: string;
  answer: string;
  sources: Source[];
}

export interface QueryRequest {
  query: string;
  top_k?: number;
  tag?: 'R' | 'G';
}

export interface ApiError {
  detail: string;
}