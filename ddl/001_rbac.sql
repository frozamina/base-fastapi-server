-- 基项目通用表：用户、角色、权限。不建物理外键，关联在应用层校验。
-- 先建库：CREATE DATABASE base_app DEFAULT CHARSET utf8mb4;
-- 应用启动时也会按模型建这些表，本文件留给手工初始化或对照结构。

CREATE TABLE IF NOT EXISTS sys_user (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  username VARCHAR(32) NOT NULL COMMENT '登录名',
  password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
  real_name VARCHAR(32) NULL COMMENT '显示姓名',
  status INT NOT NULL DEFAULT 1 COMMENT '1启用 0停用',
  is_deleted INT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0 未删除，1 已删除',
  create_time DATETIME NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  update_time DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_sys_user_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户';

CREATE TABLE IF NOT EXISTS sys_role (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  role_code VARCHAR(32) NOT NULL COMMENT '角色编码，如 admin',
  role_name VARCHAR(64) NOT NULL COMMENT '角色名称',
  description VARCHAR(255) NULL COMMENT '说明',
  is_deleted INT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0 未删除，1 已删除',
  create_time DATETIME NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  update_time DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_sys_role_code (role_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色';

CREATE TABLE IF NOT EXISTS sys_permission (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '权限主键',
  perm_code VARCHAR(64) NOT NULL COMMENT '权限编码',
  perm_name VARCHAR(64) NOT NULL COMMENT '权限名称',
  resource VARCHAR(32) NOT NULL COMMENT '资源，如 order',
  action VARCHAR(16) NOT NULL COMMENT '动作 read/write/delete/*',
  description VARCHAR(255) NULL COMMENT '说明',
  PRIMARY KEY (id),
  UNIQUE KEY uk_sys_permission_code (perm_code),
  KEY ix_sys_permission_resource (resource)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限点';

CREATE TABLE IF NOT EXISTS sys_user_role (
  id BIGINT NOT NULL AUTO_INCREMENT,
  user_id BIGINT NOT NULL COMMENT '逻辑外键：sys_user.id',
  role_id BIGINT NOT NULL COMMENT '逻辑外键：sys_role.id',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_role (user_id, role_id),
  KEY ix_sys_user_role_user_id (user_id),
  KEY ix_sys_user_role_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户与角色';

CREATE TABLE IF NOT EXISTS sys_role_permission (
  id BIGINT NOT NULL AUTO_INCREMENT,
  role_id BIGINT NOT NULL COMMENT '逻辑外键：sys_role.id',
  permission_id BIGINT NOT NULL COMMENT '逻辑外键：sys_permission.id',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_role_perm (role_id, permission_id),
  KEY ix_sys_role_permission_role_id (role_id),
  KEY ix_sys_role_permission_permission_id (permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色与权限';
