import { Connection, PublicKey, PublicKeyInitData } from '@solana/web3.js';
import {
  NameRegistryState,
  getHashedNameSync,
  getNameAccountKeySync,
} from '@bonfida/spl-name-service';
import base58 from 'bs58';
import { getAssociatedTokenAddress } from 'spl';

export const connection = new Connection(
  process.env['RPC_URL'] ??
    'https://defiland-defiland-634e.mainnet.rpcpool.com/d396f84d-a693-47f8-b3c0-3d7f72bc83e3',
);

export async function findAssociatedTokenAddress(
  walletAddress: PublicKeyInitData,
  tokenMintAddress: PublicKeyInitData,
) {
  return await getAssociatedTokenAddress(
    new PublicKey(tokenMintAddress),
    new PublicKey(walletAddress),
  );
}

export async function getLatestBlockHash(connection: Connection) {
  return connection.getLatestBlockhash();
}

export async function getTokenSupply(
  mintAddress: PublicKeyInitData,
  connection: Connection,
) {
  const tokenInfo = await connection.getTokenSupply(new PublicKey(mintAddress));

  return tokenInfo;
}

export async function getDestinationAddress(
  connection: Connection,
  destination: string,
) {
  try {
    let destinationPK: PublicKey | undefined;

    if (destination.endsWith('.sol')) {
      destinationPK = await resolveDomainName(
        connection,
        destination.slice(0, -4),
      );
      if (!destinationPK) return undefined;
    } else {
      const decoded = base58.decode(destination);

      if (decoded.length !== 32) {
        return undefined;
      }

      destinationPK = new PublicKey(destination);
    }

    return destinationPK;
  } catch (e) {
    console.error('e', e);
    return undefined;
  }
}

async function resolveDomainName(connection: Connection, domainName: string) {
  const SOL_TLD_AUTHORITY = new PublicKey(
    '58PwtjSDuFHuUkYjH9BYnnQKHfwo9reZhC2zMJv9JPkx',
  );
  const hashedDomainName = getHashedNameSync(domainName);
  const inputDomainKey = getNameAccountKeySync(
    hashedDomainName,
    undefined,
    SOL_TLD_AUTHORITY,
  );

  try {
    const { registry } = await NameRegistryState.retrieve(
      connection,
      inputDomainKey,
    );

    return registry.owner;
  } catch (err) {
    console.warn(err);
    return undefined;
  }
}
