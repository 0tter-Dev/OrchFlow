export type UserRole = "admin" | "member";

export type UserSummary = {
  id: number;
  is_active: boolean;
  role: UserRole;
  username: string;
};

export type AccessTokenPayload = {
  access_token: string;
  expires_in_seconds: number;
  token_type: string;
};
