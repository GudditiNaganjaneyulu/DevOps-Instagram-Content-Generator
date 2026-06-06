import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import GitHub from "next-auth/providers/github";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          // Request offline access so we get an access_token we can send to backend
          access_type: "offline",
          prompt: "consent",
          scope: "openid email profile",
        },
      },
    }),
    GitHub({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
  ],
  session: { strategy: "jwt" },
  callbacks: {
    async jwt({ token, account }) {
      // On first sign-in, exchange the OAuth access_token with our FastAPI backend
      if (account?.access_token && account?.provider) {
        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
          const resp = await fetch(`${apiUrl}/api/v1/auth/${account.provider}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              access_token: account.access_token,
              provider: account.provider,
            }),
          });
          if (resp.ok) {
            const data = await resp.json();
            token.backendToken = data.access_token;
            token.backendUser = data.user;
          }
        } catch {
          // Backend unavailable — session still works, API calls will fail gracefully
        }
      }
      return token;
    },
    async session({ session, token }) {
      session.backendToken = token.backendToken as string | undefined;
      session.backendUser = token.backendUser as Record<string, unknown> | undefined;
      return session;
    },
  },
  pages: { signIn: "/login" },
  trustHost: true,
});
