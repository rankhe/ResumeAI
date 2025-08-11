import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class DatabaseManager:
    """数据库管理器，负责存储和管理简历生成历史"""
    
    def __init__(self, db_path: str = "resume_ai.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建生成历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_title TEXT NOT NULL,
                    company_name TEXT,
                    generation_type TEXT NOT NULL,  -- 'description', 'url', 'template'
                    input_data TEXT,  -- JSON格式存储输入数据
                    output_file_path TEXT,
                    match_score REAL,
                    optimization_suggestions TEXT,  -- JSON格式存储优化建议
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建用户配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建简历模板使用统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS template_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def save_generation_record(self, 
                             job_title: str,
                             company_name: str,
                             generation_type: str,
                             input_data: Dict,
                             output_file_path: str,
                             match_score: float = 0.0,
                             optimization_suggestions: List[str] = None) -> int:
        """
        保存简历生成记录
        
        Args:
            job_title: 职位标题
            company_name: 公司名称
            generation_type: 生成类型
            input_data: 输入数据
            output_file_path: 输出文件路径
            match_score: 匹配分数
            optimization_suggestions: 优化建议
            
        Returns:
            记录ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO generation_history 
                (job_title, company_name, generation_type, input_data, 
                 output_file_path, match_score, optimization_suggestions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_title,
                company_name,
                generation_type,
                json.dumps(input_data, ensure_ascii=False),
                output_file_path,
                match_score,
                json.dumps(optimization_suggestions or [], ensure_ascii=False)
            ))
            
            record_id = cursor.lastrowid
            conn.commit()
            return record_id
    
    def get_generation_history(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        获取生成历史记录
        
        Args:
            limit: 返回记录数量限制
            offset: 偏移量
            
        Returns:
            历史记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, job_title, company_name, generation_type, 
                       input_data, output_file_path, match_score, 
                       optimization_suggestions, created_at
                FROM generation_history
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            records = []
            for row in cursor.fetchall():
                record = {
                    "id": row[0],
                    "job_title": row[1],
                    "company_name": row[2],
                    "generation_type": row[3],
                    "input_data": json.loads(row[4]) if row[4] else {},
                    "output_file_path": row[5],
                    "match_score": row[6],
                    "optimization_suggestions": json.loads(row[7]) if row[7] else [],
                    "created_at": row[8]
                }
                records.append(record)
            
            return records
    
    def get_generation_record_by_id(self, record_id: int) -> Optional[Dict]:
        """
        根据ID获取生成记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            记录详情，如果不存在返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, job_title, company_name, generation_type, 
                       input_data, output_file_path, match_score, 
                       optimization_suggestions, created_at
                FROM generation_history
                WHERE id = ?
            ''', (record_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "job_title": row[1],
                    "company_name": row[2],
                    "generation_type": row[3],
                    "input_data": json.loads(row[4]) if row[4] else {},
                    "output_file_path": row[5],
                    "match_score": row[6],
                    "optimization_suggestions": json.loads(row[7]) if row[7] else [],
                    "created_at": row[8]
                }
            return None
    
    def delete_generation_record(self, record_id: int) -> bool:
        """
        删除生成记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            是否删除成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM generation_history WHERE id = ?', (record_id,))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def search_generation_history(self, keyword: str, limit: int = 50) -> List[Dict]:
        """
        搜索生成历史
        
        Args:
            keyword: 搜索关键词
            limit: 返回记录数量限制
            
        Returns:
            匹配的历史记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, job_title, company_name, generation_type, 
                       input_data, output_file_path, match_score, 
                       optimization_suggestions, created_at
                FROM generation_history
                WHERE job_title LIKE ? OR company_name LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (f'%{keyword}%', f'%{keyword}%', limit))
            
            records = []
            for row in cursor.fetchall():
                record = {
                    "id": row[0],
                    "job_title": row[1],
                    "company_name": row[2],
                    "generation_type": row[3],
                    "input_data": json.loads(row[4]) if row[4] else {},
                    "output_file_path": row[5],
                    "match_score": row[6],
                    "optimization_suggestions": json.loads(row[7]) if row[7] else [],
                    "created_at": row[8]
                }
                records.append(record)
            
            return records
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计数据
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 总生成次数
            cursor.execute('SELECT COUNT(*) FROM generation_history')
            total_generations = cursor.fetchone()[0]
            
            # 按类型统计
            cursor.execute('''
                SELECT generation_type, COUNT(*) 
                FROM generation_history 
                GROUP BY generation_type
            ''')
            type_stats = dict(cursor.fetchall())
            
            # 平均匹配分数
            cursor.execute('SELECT AVG(match_score) FROM generation_history WHERE match_score > 0')
            avg_match_score = cursor.fetchone()[0] or 0.0
            
            # 最近7天的生成次数
            cursor.execute('''
                SELECT COUNT(*) FROM generation_history 
                WHERE created_at >= datetime('now', '-7 days')
            ''')
            recent_generations = cursor.fetchone()[0]
            
            return {
                "total_generations": total_generations,
                "type_statistics": type_stats,
                "average_match_score": round(avg_match_score, 2),
                "recent_generations": recent_generations
            }
    
    def update_template_usage(self, template_id: str):
        """
        更新模板使用统计
        
        Args:
            template_id: 模板ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在记录
            cursor.execute('SELECT usage_count FROM template_usage WHERE template_id = ?', (template_id,))
            result = cursor.fetchone()
            
            if result:
                # 更新使用次数
                cursor.execute('''
                    UPDATE template_usage 
                    SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE template_id = ?
                ''', (template_id,))
            else:
                # 插入新记录
                cursor.execute('''
                    INSERT INTO template_usage (template_id, usage_count, last_used)
                    VALUES (?, 1, CURRENT_TIMESTAMP)
                ''', (template_id,))
            
            conn.commit()
    
    def get_template_usage_stats(self) -> List[Dict]:
        """
        获取模板使用统计
        
        Returns:
            模板使用统计列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT template_id, usage_count, last_used
                FROM template_usage
                ORDER BY usage_count DESC
            ''')
            
            stats = []
            for row in cursor.fetchall():
                stats.append({
                    "template_id": row[0],
                    "usage_count": row[1],
                    "last_used": row[2]
                })
            
            return stats
    
    def save_user_setting(self, key: str, value: str):
        """
        保存用户设置
        
        Args:
            key: 设置键
            value: 设置值
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_settings (setting_key, setting_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            
            conn.commit()
    
    def get_user_setting(self, key: str, default_value: str = None) -> Optional[str]:
        """
        获取用户设置
        
        Args:
            key: 设置键
            default_value: 默认值
            
        Returns:
            设置值
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT setting_value FROM user_settings WHERE setting_key = ?', (key,))
            result = cursor.fetchone()
            
            return result[0] if result else default_value

# 使用示例
if __name__ == "__main__":
    db = DatabaseManager()
    
    # 保存生成记录
    record_id = db.save_generation_record(
        job_title="Python开发工程师",
        company_name="科技公司",
        generation_type="description",
        input_data={"description": "招聘Python开发工程师"},
        output_file_path="resume_001.pdf",
        match_score=85.5,
        optimization_suggestions=["增加Python项目经验", "补充数据库技能"]
    )
    
    print(f"保存记录ID: {record_id}")
    
    # 获取统计信息
    stats = db.get_statistics()
    print(f"统计信息: {stats}")