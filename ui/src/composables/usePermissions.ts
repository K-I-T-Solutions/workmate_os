/**
 * Permission checking composable
 * Provides utility functions to check if the current user has specific permissions
 */

import { useAuth } from './useAuth';

export function usePermissions() {
  const { user } = useAuth();

  /**
   * Check if user has a specific permission
   * Supports wildcards: "*" (all permissions), "module.*" (all module permissions)
   */
  const hasPermission = (permission: string): boolean => {
    if (!user.value) return false;

    const permissions = user.value.permissions || [];

    // Check for global wildcard
    if (permissions.includes('*')) return true;

    // Check exact match
    if (permissions.includes(permission)) return true;

    // Check prefix wildcard (e.g., "admin.*" matches "admin.employees.view")
    return permissions.some((perm: string) => {
      if (perm.endsWith('.*')) {
        const prefix = perm.slice(0, -2);
        return permission.startsWith(prefix + '.');
      }
      return false;
    });
  };

  /**
   * Check if user has at least one of the provided permissions
   */
  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissions.some(hasPermission);
  };

  /**
   * Check if user has all of the provided permissions
   */
  const hasAllPermissions = (permissions: string[]): boolean => {
    return permissions.every(hasPermission);
  };

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  };
}
