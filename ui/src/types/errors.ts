/**
 * WorkmateOS Error Types
 *
 * Definiert die Struktur der Error Responses vom Backend
 */

/**
 * Strukturierter Error Response vom Backend
 *
 * @example
 * {
 *   "error_code": "AUTH_1002",
 *   "message": "Ihr Sitzungstoken ist ungültig.",
 *   "hint": "Bitte melden Sie sich erneut an."
 * }
 */
export interface ErrorDetail {
  /** Eindeutiger Error Code (z.B. AUTH_1002, INVOICE_2001) */
  error_code: string;

  /** Benutzerfreundliche Fehlermeldung (Deutsch) */
  message: string;

  /** Optional: Hilfreicher Hinweis für den User */
  hint?: string;
}

/**
 * API Error Response
 *
 * Das Backend kann entweder einen strukturierten Error (ErrorDetail)
 * oder einen einfachen String zurückgeben (Legacy)
 */
export interface APIErrorResponse {
  /** Error Details - kann Object oder String sein */
  detail: ErrorDetail | string;
}

/**
 * Type Guard: Prüft ob detail ein strukturierter Error ist
 */
export function isStructuredError(detail: unknown): detail is ErrorDetail {
  return (
    typeof detail === 'object' &&
    detail !== null &&
    'error_code' in detail &&
    'message' in detail &&
    typeof (detail as ErrorDetail).error_code === 'string' &&
    typeof (detail as ErrorDetail).message === 'string'
  );
}

/**
 * Error Code Kategorien
 */
export enum ErrorCategory {
  AUTH = '1xxx',
  INVOICE = '2xxx',
  FINANCE = '3xxx',
  CRM = '4xxx',
  PROJECT = '5xxx',
  DOCUMENT = '6xxx',
  DASHBOARD = '7xxx',
  REMINDER = '8xxx',
  SYSTEM = '9xxx',
}

/**
 * Bekannte Error Codes (aus Backend)
 */
export const ErrorCodes = {
  // Authentication & Authorization (1xxx)
  AUTH_NOT_AUTHENTICATED: 'AUTH_1001',
  AUTH_INVALID_TOKEN: 'AUTH_1002',
  AUTH_EXPIRED_TOKEN: 'AUTH_1003',
  AUTH_INVALID_CREDENTIALS: 'AUTH_1007',
  AUTH_INSUFFICIENT_PERMISSIONS: 'AUTH_1009',

  // Invoices (2xxx)
  INVOICE_NOT_FOUND: 'INVOICE_2001',
  INVOICE_ALREADY_PAID: 'INVOICE_2002',
  INVOICE_NUMBER_EXISTS: 'INVOICE_2005',
  INVOICE_PDF_FAILED: 'INVOICE_2009',

  // Payments (2xxx)
  PAYMENT_NOT_FOUND: 'PAYMENT_2050',
  PAYMENT_EXCEEDS_AMOUNT: 'PAYMENT_2051',

  // System (9xxx)
  SYSTEM_ERROR: 'SYSTEM_9000',
} as const;

export type ErrorCode = typeof ErrorCodes[keyof typeof ErrorCodes];
