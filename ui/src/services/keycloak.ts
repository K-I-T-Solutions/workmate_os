/**
 * Keycloak OIDC Service
 * Handles OAuth2 Authorization Code Flow with PKCE
 */

const KEYCLOAK_URL = import.meta.env.VITE_KEYCLOAK_URL || 'https://login.intern.phudevelopement.xyz';
const KEYCLOAK_REALM = import.meta.env.VITE_KEYCLOAK_REALM || 'kit';
const KEYCLOAK_CLIENT_ID = import.meta.env.VITE_KEYCLOAK_CLIENT_ID || '';
const REDIRECT_URI = `${window.location.origin}/auth/callback`;

// Keycloak OIDC endpoints
const AUTH_ENDPOINT = `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/auth`;
const TOKEN_ENDPOINT = `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/token`;

// Storage keys
const STATE_KEY = 'keycloak_oauth_state';
const VERIFIER_KEY = 'keycloak_code_verifier';
const REDIRECT_KEY = 'keycloak_redirect_after_login';

/**
 * Generate a random string for OAuth state and PKCE
 */
function generateRandomString(length: number): string {
  const array = new Uint8Array(length);
  crypto.getRandomValues(array);
  return Array.from(array, (byte) => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * Generate PKCE code verifier
 */
function generateCodeVerifier(): string {
  return generateRandomString(32);
}

/**
 * Generate PKCE code challenge from verifier
 */
async function generateCodeChallenge(verifier: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const hash = await crypto.subtle.digest('SHA-256', data);

  // Convert to base64url
  return btoa(String.fromCharCode(...new Uint8Array(hash)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

/**
 * Initiate Keycloak SSO login
 */
export async function initiateKeycloakLogin(redirectAfterLogin?: string): Promise<void> {
  // Generate state and PKCE verifier
  const state = generateRandomString(16);
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = await generateCodeChallenge(codeVerifier);

  // Store state and verifier for callback validation
  sessionStorage.setItem(STATE_KEY, state);
  sessionStorage.setItem(VERIFIER_KEY, codeVerifier);
  if (redirectAfterLogin) {
    sessionStorage.setItem(REDIRECT_KEY, redirectAfterLogin);
  }

  // Build authorization URL
  const authUrl = new URL(AUTH_ENDPOINT);
  authUrl.searchParams.set('client_id', KEYCLOAK_CLIENT_ID);
  authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('scope', 'openid profile email');
  authUrl.searchParams.set('state', state);
  authUrl.searchParams.set('code_challenge', codeChallenge);
  authUrl.searchParams.set('code_challenge_method', 'S256');

  // Redirect to Keycloak
  window.location.href = authUrl.toString();
}

/**
 * Handle OAuth callback and exchange code for token
 */
export async function handleKeycloakCallback(
  code: string,
  state: string
): Promise<{ id_token: string; access_token: string } | null> {
  // Validate state
  const storedState = sessionStorage.getItem(STATE_KEY);
  if (!storedState || storedState !== state) {
    console.error('Invalid OAuth state');
    return null;
  }

  // Get code verifier
  const codeVerifier = sessionStorage.getItem(VERIFIER_KEY);
  if (!codeVerifier) {
    console.error('Missing PKCE code verifier');
    return null;
  }

  try {
    // Exchange authorization code for tokens
    const response = await fetch(TOKEN_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: KEYCLOAK_CLIENT_ID,
        code,
        redirect_uri: REDIRECT_URI,
        code_verifier: codeVerifier,
      }),
    });

    if (!response.ok) {
      console.error('Token exchange failed:', await response.text());
      return null;
    }

    const data = await response.json();

    // Clean up session storage
    sessionStorage.removeItem(STATE_KEY);
    sessionStorage.removeItem(VERIFIER_KEY);

    return {
      id_token: data.id_token,
      access_token: data.access_token
    };
  } catch (error) {
    console.error('Error during token exchange:', error);
    return null;
  }
}

/**
 * Get redirect URL after login (if set)
 */
export function getPostLoginRedirect(): string | null {
  const redirect = sessionStorage.getItem(REDIRECT_KEY);
  sessionStorage.removeItem(REDIRECT_KEY);
  return redirect;
}
