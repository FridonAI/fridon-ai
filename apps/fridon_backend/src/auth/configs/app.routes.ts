const authRoot = 'auth';

export const authRoutes = {
  root: authRoot,
  signIn: '/sign-in',
  signUp: '/sign-up',
  getNonce: '/nonce/:walletAddress',
} as const;
