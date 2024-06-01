import { PublicKey } from '@metaplex-foundation/js';
import { Connection } from '@solana/web3.js';
import {
  getHashedNameSync,
  getNameAccountKeySync,
  NameRegistryState,
} from '@bonfida/spl-name-service';
import base58 from 'bs58';

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
