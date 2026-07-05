export interface DocumentResponse {
    filename: string;
    file_type: string;
    pages: number;
    language: string;
    language_code: string;
    ocr_used: boolean;
    characters: number;
    preview: string;
    text: string;
  }