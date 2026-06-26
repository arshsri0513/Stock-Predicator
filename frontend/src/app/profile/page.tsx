/**
 * Profile page -- placeholder until Phase 12 builds real authentication.
 * We build the shell now so the navbar link has somewhere real to go,
 * and so the layout/styling pattern is already established for Phase 12
 * to fill in with real user data, watchlist, and settings.
 */
export default function ProfilePage() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-8">
      <h1 className="text-2xl font-bold">Profile</h1>
      <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
        Account settings, watchlist, and prediction history.
      </p>

      <div
        className="mt-8 rounded-lg border p-6 text-center"
        style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
      >
        <p style={{ color: "var(--text-secondary)" }}>
          Sign-up and login aren&apos;t built yet -- this arrives in Phase 12.
        </p>
        <p className="mt-2 text-sm" style={{ color: "var(--text-secondary)" }}>
          Once authentication exists, this page will show your saved watchlist,
          past predictions, and account settings.
        </p>
      </div>
    </main>
  );
}
