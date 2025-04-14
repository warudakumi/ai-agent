'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Sidebar.module.css';

const Sidebar = () => {
  const pathname = usePathname();
  
  // ナビゲーション項目
  const navItems = [
    { path: '/chat', label: 'チャット' },
    { path: '/settings', label: '設定' },
  ];
  
  return (
    <div className={styles.sidebar}>
      <div className={styles.logoContainer}>
        <Link href="/">
          <img src="/images/logo.png" alt="Agent Logo" height="40" />
        </Link>
      </div>
      
      <nav className={styles.nav}>
        {navItems.map((item) => (
          <Link
            key={item.path}
            href={item.path}
            className={`${styles.navItem} ${pathname === item.path ? styles.active : ''}`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      
      <div className={styles.footer}>
        <p className={styles.copyright}>© 2025 copyright placeholder</p>
      </div>
    </div>
  );
};

export default Sidebar;