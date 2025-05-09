// Chat Examples
// todo: move this to db
export function getWeightedExamples(limit: number): ChatExampleType[] {
  const results: ChatExampleType[] = [];
  const pool = [...CHAT_EXAMPLES];

  while (results.length < limit && pool.length > 0) {
    const totalWeight = pool.reduce((sum, ex) => sum + ex.weight, 0);
    let rand = Math.random() * totalWeight;

    const index = pool.findIndex((example) => {
      if (rand < example.weight) return true;
      rand -= example.weight;
      return false;
    });

    if (index !== -1) {
      results.push(pool[index]!);
      pool.splice(index, 1);
    }
  }

  return results;
}
export type ChatExampleType = {
  message: string;
  weight: number;
};

export const CHAT_EXAMPLES: ChatExampleType[] = [
  {
    message: 'Analyze sol price chart',
    weight: 0.5,
  },
  {
    message: 'Analyze Bitcoins Halving cycles',
    weight: 0.5,
  },
  {
    message: 'What is the price of Bitcoin?',
    weight: 0.5,
  },
  {
    message: 'What is the price of Solana?',
    weight: 0.5,
  },
  {
    message: 'What is the price of Ethereum?',
    weight: 0.5,
  },
  {
    message: 'What is the price of Dogecoin?',
    weight: 0.5,
  },
  {
    message: 'What is the price of Shiba Inu?',
    weight: 0.5,
  },
  {
    message: 'What is the price of Cardano?',
    weight: 0.5,
  },
  {
    message: 'What is the price of Polkadot?',
    weight: 0.5,
  },
  {
    message: 'What is the price of Chainlink?',
    weight: 0.5,
  },
];

// Model Examples
// todo: move this to db
export type ModelExampleType = {
  name: string;
  slug: string;
  icon: string;
};

export const MODEL_EXAMPLES: ModelExampleType[] = [
  {
    name: 'Deepseek',
    slug: 'deepseek',
    icon: 'https://cdn.discordapp.com/attachments/1111111111111111111/1111111111111111111/deepseek.png',
  },
  {
    name: 'OpenAI',
    slug: 'openai',
    icon: 'https://cdn.discordapp.com/attachments/1111111111111111111/1111111111111111111/openai.png',
  },
  {
    name: 'Anthropic',
    slug: 'anthropic',
    icon: 'https://cdn.discordapp.com/attachments/1111111111111111111/1111111111111111111/anthropic.png',
  },
  {
    name: 'CodeGeeX',
    slug: 'codegeex',
    icon: 'https://cdn.discordapp.com/attachments/1111111111111111111/1111111111111111111/codegeex.png',
  },
  {
    name: 'Gemini',
    slug: 'gemini',
    icon: 'https://cdn.discordapp.com/attachments/1111111111111111111/1111111111111111111/gemini.png',
  },
];
