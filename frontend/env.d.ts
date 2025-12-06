/// <reference types="vite/client" />

// Declaración global para variables de entorno en runtime
declare global {
  interface Window {
    __env?: {
      VITE_API_URL?: string;
    };
  }
}
