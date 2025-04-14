import { SettingsProvider } from '@/context/SettingsContext';
import '../styles/globals.css';

export const metadata = {
  title: 'AI Agent',
  description: 'インテリジェントなAIエージェント',
};

export default function RootLayout({ children }) {
  return (
    <html lang="ja">
      <body>
        <SettingsProvider>
          {children}
        </SettingsProvider>
      </body>
    </html>
  );
}