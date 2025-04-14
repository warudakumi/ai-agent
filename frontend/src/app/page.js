'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import styles from './page.module.css';

export default function Home() {
  const router = useRouter();
  
  // 自動的にチャットページにリダイレクト
  useEffect(() => {
    router.push('/chat');
  }, [router]);
  
  return (
    <div className={styles.container}>
      <div className={styles.loading}>
        <div className={styles.logo}>
          <Image src="/images/logo.png" alt="Agent Logo" width={200} height={50} priority />
        </div>
        <p>読み込み中...</p>
      </div>
    </div>
  );
}