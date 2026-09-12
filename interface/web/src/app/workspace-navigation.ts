import type { UserRole } from "../shared/types/auth";

export type NavigationItem = {
  label: string;
  to: string;
};

export function workspaceNavigationItems(
  role: UserRole,
  copy: Record<string, string>,
): NavigationItem[] {
  const items = [
    { label: copy.overview, to: "/overview" },
    { label: copy.projects, to: "/projects" },
    { label: copy.ai, to: "/ai" },
    { label: copy.activity, to: "/activity" },
    { label: copy.settings, to: "/settings" },
    { label: copy.profile, to: "/profile" },
  ];

  return role === "admin" ? [...items, { label: copy.admin, to: "/admin" }] : items;
}
