"use client";

import { motion } from "framer-motion";

interface CommitmentLoopProps {
  className?: string;
}

export function CommitmentLoop({ className }: CommitmentLoopProps) {
  const circleRadius = 100;
  const centerX = 200;
  const centerY = 200;

  const nodes: Array<{
    cx: number;
    cy: number;
    label: string;
    labelX?: number;
    labelY?: number;
    labelAnchor: "start" | "middle" | "end";
  }> = [
    { cx: centerX, cy: centerY - circleRadius, label: "Plan", labelY: centerY - circleRadius - 20, labelAnchor: "middle" },
    { cx: centerX + circleRadius, cy: centerY, label: "Act", labelX: centerX + circleRadius + 20, labelY: centerY + 4, labelAnchor: "start" },
    { cx: centerX, cy: centerY + circleRadius, label: "Observe", labelY: centerY + circleRadius + 20, labelAnchor: "middle" },
    { cx: centerX - circleRadius, cy: centerY, label: "Adapt", labelX: centerX - circleRadius - 20, labelY: centerY + 4, labelAnchor: "end" },
  ];

  return (
    <motion.div
      className={`relative ${className}`}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8 }}
      whileHover={{ scale: 1.05 }}
      style={{ perspective: "1000px" }}
    >
      <svg
        viewBox="0 0 400 400"
        className="w-full h-full"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Gradient definitions */}
          <linearGradient id="primaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="hsl(164, 94%, 43%)" stopOpacity="0.9" />
            <stop offset="50%" stopColor="hsl(199, 89%, 58%)" stopOpacity="0.8" />
            <stop offset="100%" stopColor="hsl(262, 52%, 47%)" stopOpacity="0.9" />
          </linearGradient>
          
          <linearGradient id="secondaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="hsl(199, 89%, 58%)" stopOpacity="0.6" />
            <stop offset="100%" stopColor="hsl(164, 94%, 43%)" stopOpacity="0.8" />
          </linearGradient>
          
          <radialGradient id="glowGradient" cx="50%" cy="50%">
            <stop offset="0%" stopColor="hsl(164, 94%, 43%)" stopOpacity="0.4" />
            <stop offset="100%" stopColor="hsl(164, 94%, 43%)" stopOpacity="0" />
          </radialGradient>
          
          {/* Glow filter */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          
          {/* Shadow filter */}
          <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="0" stdDeviation="8" floodColor="hsl(164, 94%, 43%)" floodOpacity="0.3" />
          </filter>
        </defs>

        {/* Animated background glow */}
        <motion.circle
          cx={centerX}
          cy={centerY}
          r={circleRadius + 30}
          fill="url(#glowGradient)"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{
            scale: [0.8, 1.1, 0.8],
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        />

        {/* Outer orbit - main loop */}
        <motion.circle
          cx={centerX}
          cy={centerY}
          r={circleRadius}
          stroke="url(#primaryGradient)"
          strokeWidth="3"
          fill="none"
          filter="url(#glow)"
          initial={{ pathLength: 0, opacity: 0, rotate: -90 }}
          animate={{
            pathLength: 1,
            opacity: 0.8,
            rotate: 0,
          }}
          transition={{
            pathLength: { duration: 2, ease: "easeInOut" },
            opacity: { duration: 1.5 },
            rotate: { duration: 2, ease: "easeInOut" },
          }}
          style={{ transformOrigin: "200px 200px" }}
        />

        {/* Inner orbit - secondary loop */}
        <motion.circle
          cx={centerX}
          cy={centerY}
          r={circleRadius - 30}
          stroke="url(#secondaryGradient)"
          strokeWidth="2.5"
          fill="none"
          opacity={0.6}
          initial={{ pathLength: 0, rotate: 90 }}
          animate={{
            pathLength: 1,
            rotate: 360,
          }}
          transition={{
            pathLength: { duration: 2.5, ease: "easeInOut", delay: 0.3 },
            rotate: { duration: 20, repeat: Infinity, ease: "linear" },
          }}
          style={{ transformOrigin: "200px 200px" }}
        />

        {/* Connection lines with gradients */}
        {[
          { start: { x: centerX, y: centerY - circleRadius }, end: { x: centerX, y: centerY - circleRadius + 25 } },
          { start: { x: centerX + circleRadius, y: centerY }, end: { x: centerX + circleRadius - 25, y: centerY } },
          { start: { x: centerX, y: centerY + circleRadius }, end: { x: centerX, y: centerY + circleRadius - 25 } },
          { start: { x: centerX - circleRadius, y: centerY }, end: { x: centerX - circleRadius + 25, y: centerY } },
        ].map((line, i) => (
          <motion.line
            key={i}
            x1={line.start.x}
            y1={line.start.y}
            x2={line.end.x}
            y2={line.end.y}
            stroke="url(#primaryGradient)"
            strokeWidth="2.5"
            strokeLinecap="round"
            filter="url(#glow)"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.7 }}
            transition={{ duration: 1, delay: 0.5 + i * 0.2 }}
          />
        ))}

        {/* Animated nodes */}
        {nodes.map((node, i) => (
          <g key={i}>
            {/* Outer glow */}
            <motion.circle
              cx={node.cx}
              cy={node.cy}
              r="10"
              fill="url(#glowGradient)"
              initial={{ scale: 0, opacity: 0 }}
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.4, 0.7, 0.4],
              }}
              transition={{
                scale: { duration: 2, repeat: Infinity, delay: 1.2 + i * 0.1 },
                opacity: { duration: 2, repeat: Infinity, delay: 1.2 + i * 0.1 },
              }}
            />
            {/* Main node */}
            <motion.circle
              cx={node.cx}
              cy={node.cy}
              r="8"
              fill="url(#primaryGradient)"
              filter="url(#shadow)"
              initial={{ scale: 0, opacity: 0 }}
              animate={{
                scale: 1,
                opacity: 1,
              }}
              transition={{ duration: 0.5, delay: 1.2 + i * 0.1, type: "spring", stiffness: 200 }}
              whileHover={{ scale: 1.3 }}
            />
            {/* Inner highlight */}
            <circle
              cx={node.cx}
              cy={node.cy}
              r="4"
              fill="hsl(210, 30%, 98%)"
              opacity="0.6"
            />
            {/* Label */}
            <text
              x={node.labelX ?? node.cx}
              y={node.labelY ?? node.cy}
              textAnchor={node.labelAnchor}
              fill="hsl(210, 30%, 98%)"
              fontSize="13"
              fontWeight="600"
              opacity="0.9"
              style={{
                filter: "drop-shadow(0 0 4px hsl(164, 94%, 43%))",
              }}
            >
              {node.label}
            </text>
          </g>
        ))}

        {/* Central hub with pulsing glow */}
        <motion.g>
          <motion.circle
            cx={centerX}
            cy={centerY}
            r="12"
            fill="url(#glowGradient)"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 0.8, 0.5],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
          <circle
            cx={centerX}
            cy={centerY}
            r="6"
            fill="url(#primaryGradient)"
            filter="url(#shadow)"
            opacity="0.9"
          />
          <circle
            cx={centerX}
            cy={centerY}
            r="3"
            fill="hsl(210, 30%, 98%)"
            opacity="0.8"
          />
        </motion.g>

        {/* Floating particles */}
        {Array.from({ length: 6 }).map((_, i) => {
          const angle = (i * 60) * (Math.PI / 180);
          const distance = circleRadius + 40;
          const particleX = centerX + Math.cos(angle) * distance;
          const particleY = centerY + Math.sin(angle) * distance;
          
          return (
            <motion.circle
              key={i}
              cx={particleX}
              cy={particleY}
              r="3"
              fill="url(#secondaryGradient)"
              initial={{ opacity: 0, scale: 0 }}
              animate={{
                opacity: [0, 0.8, 0],
                scale: [0, 1.5, 0],
                y: [particleY, particleY - 20, particleY],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                delay: i * 0.5,
                ease: "easeInOut",
              }}
              filter="url(#glow)"
            />
          );
        })}
      </svg>
    </motion.div>
  );
}
