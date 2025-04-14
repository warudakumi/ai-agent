'use client';

import React from 'react';
import Link from 'next/link';
import styles from './Header.module.css';

const Header = () => {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <Link href="/">
          <img src="/images/logo.png" alt="Agent Logo" height="36" />
        </Link>
      </div>
      <nav className={styles.nav}>
        <Link href="/chat" className={styles.navLink}>
          チャット
        </Link>
        <Link href="/settings" className={styles.navLink}>
          設定
        </Link>
      </nav>
    </header>
  );
};

export default Header;