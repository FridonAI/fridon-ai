import { PublicKey } from '@metaplex-foundation/js';
import { LAMPORTS_PER_SOL } from '@solana/web3.js';

export const SOL_MINT_ADDRESS = new PublicKey(
  '11111111111111111111111111111111',
);
export const WSOL_MINT_ADDRESS = new PublicKey(
  'So11111111111111111111111111111111111111112',
);

export const KAMINO_MAIN_MARKET_ADDRESS = new PublicKey(
  '7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF',
);

export const USDC_MINT_ADDRESS = new PublicKey(
  'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
);

export const DONATION_ADDRESS = new PublicKey(
  '4aTrKPtTRFXbqFHSKdtn6R2LgvLWkFeeNQ3C9mFAu8qs',
);

export const SWAP_REFERRAL_PROGRAM_ADDRESS = new PublicKey(
  'REFER4ZgmyYx9c6He5XfaTMiGfdLwRnkV4RPp9t9iF3',
);

export const PRIORITY_FEE = 0.005 * LAMPORTS_PER_SOL;
export const COMPUTE_LIMIT = 400000;
export const SWAP_FEE_BPS = 7;
export const DEFAULT_SLIPPAGE = 0.5;
export const NEW_TOKEN_FEE = 2039280;
export const TRANSFER_FEE = 5000;
