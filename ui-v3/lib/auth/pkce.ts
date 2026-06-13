const KEYCLOAK_URL = process.env.NEXT_PUBLIC_KEYCLOAK_URL!
const KEYCLOAK_REALM = process.env.NEXT_PUBLIC_KEYCLOAK_REALM!
const KEYCLOAK_CLIENT_ID = process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID!
const APP_URL = process.env.NEXT_PUBLIC_APP_URL ?? (typeof window !== "undefined" ? window.location.origin : "")

export const ISSUER = `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}`
const AUTH_ENDPOINT = `${ISSUER}/protocol/openid-connect/auth`
const TOKEN_ENDPOINT = `${ISSUER}/protocol/openid-connect/token`
const LOGOUT_ENDPOINT = `${ISSUER}/protocol/openid-connect/logout`

const STATE_KEY = "oidc_state"
const VERIFIER_KEY = "oidc_verifier"
const REDIRECT_KEY = "oidc_redirect"

// Pure-JS SHA-256 — no crypto.subtle, works on HTTP / non-secure contexts
export function sha256hex(text: string): string {
  const bytes = new TextEncoder().encode(text)
  const out = sha256(bytes)
  return Array.from(out).map(b => b.toString(16).padStart(2, "0")).join("")
}

function sha256(message: Uint8Array): Uint8Array {
  const K = [
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2,
  ]
  let h = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]
  const l = message.length
  const bitLen = l * 8
  const padLen = l % 64 < 56 ? 56 - (l % 64) : 120 - (l % 64)
  const buf = new Uint8Array(l + padLen + 8)
  buf.set(message)
  buf[l] = 0x80
  const view = new DataView(buf.buffer)
  view.setUint32(buf.length - 4, bitLen >>> 0, false)
  view.setUint32(buf.length - 8, Math.floor(bitLen / 2 ** 32), false)

  const r = (x: number, n: number) => (x >>> n) | (x << (32 - n))
  for (let i = 0; i < buf.length; i += 64) {
    const w = new Array(64)
    for (let j = 0; j < 16; j++) w[j] = view.getUint32(i + j * 4, false)
    for (let j = 16; j < 64; j++) {
      const s0 = r(w[j-15],7) ^ r(w[j-15],18) ^ (w[j-15] >>> 3)
      const s1 = r(w[j-2],17) ^ r(w[j-2],19) ^ (w[j-2] >>> 10)
      w[j] = (w[j-16] + s0 + w[j-7] + s1) >>> 0
    }
    let [a,b,c,d,e,f,g,hh] = h
    for (let j = 0; j < 64; j++) {
      const S1 = r(e,6) ^ r(e,11) ^ r(e,25)
      const ch = (e & f) ^ (~e & g)
      const t1 = (hh + S1 + ch + K[j] + w[j]) >>> 0
      const S0 = r(a,2) ^ r(a,13) ^ r(a,22)
      const maj = (a & b) ^ (a & c) ^ (b & c)
      const t2 = (S0 + maj) >>> 0
      hh=g; g=f; f=e; e=(d+t1)>>>0; d=c; c=b; b=a; a=(t1+t2)>>>0
    }
    h = h.map((v, i) => (v + [a,b,c,d,e,f,g,hh][i]) >>> 0)
  }
  const out = new Uint8Array(32)
  const outView = new DataView(out.buffer)
  h.forEach((v, i) => outView.setUint32(i * 4, v, false))
  return out
}

function toBase64url(bytes: Uint8Array): string {
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=/g, "")
}

function randomString(length: number): string {
  const arr = new Uint8Array(length)
  crypto.getRandomValues(arr)
  return Array.from(arr, (b) => b.toString(16).padStart(2, "0")).join("")
}

function codeChallenge(verifier: string): string {
  return toBase64url(sha256(new TextEncoder().encode(verifier)))
}

const REDIRECT_URI = `${APP_URL}/auth/callback`

export function startLogin(redirectAfter?: string) {
  const state = randomString(16)
  const verifier = randomString(32)
  const challenge = codeChallenge(verifier)

  sessionStorage.setItem(STATE_KEY, state)
  sessionStorage.setItem(VERIFIER_KEY, verifier)
  if (redirectAfter) sessionStorage.setItem(REDIRECT_KEY, redirectAfter)

  const url = new URL(AUTH_ENDPOINT)
  url.searchParams.set("client_id", KEYCLOAK_CLIENT_ID)
  url.searchParams.set("redirect_uri", REDIRECT_URI)
  url.searchParams.set("response_type", "code")
  url.searchParams.set("scope", "openid profile email")
  url.searchParams.set("state", state)
  url.searchParams.set("code_challenge", challenge)
  url.searchParams.set("code_challenge_method", "S256")

  window.location.href = url.toString()
}

export async function exchangeCode(
  code: string,
  state: string
): Promise<{ access_token: string; id_token: string; refresh_token?: string } | null> {
  const storedState = sessionStorage.getItem(STATE_KEY)
  const verifier = sessionStorage.getItem(VERIFIER_KEY)
  if (!storedState || storedState !== state || !verifier) return null

  const res = await fetch(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      client_id: KEYCLOAK_CLIENT_ID,
      code,
      redirect_uri: REDIRECT_URI,
      code_verifier: verifier,
    }),
  })

  if (!res.ok) return null
  const data = await res.json()

  sessionStorage.removeItem(STATE_KEY)
  sessionStorage.removeItem(VERIFIER_KEY)

  return { access_token: data.access_token, id_token: data.id_token, refresh_token: data.refresh_token }
}

export function popRedirect(): string {
  const r = sessionStorage.getItem(REDIRECT_KEY) ?? "/dashboard"
  sessionStorage.removeItem(REDIRECT_KEY)
  return r
}

export function buildLogoutUrl(idToken: string): string {
  const url = new URL(LOGOUT_ENDPOINT)
  url.searchParams.set("id_token_hint", idToken)
  url.searchParams.set("post_logout_redirect_uri", APP_URL + "/login")
  return url.toString()
}

export async function refreshTokens(
  refreshToken: string
): Promise<{ access_token: string; id_token: string; refresh_token?: string } | null> {
  try {
    const res = await fetch(TOKEN_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "refresh_token",
        client_id: KEYCLOAK_CLIENT_ID,
        refresh_token: refreshToken,
      }),
    })
    if (!res.ok) return null
    const data = await res.json()
    return { access_token: data.access_token, id_token: data.id_token, refresh_token: data.refresh_token }
  } catch {
    return null
  }
}
