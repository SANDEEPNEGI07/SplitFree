import api from './api';

// Get group history
export const getGroupHistory = async (groupId) => {
  try {
    const response = await api.get(`/group/${groupId}/history`);
    return response.data;
  } catch (error) {
    console.error('Error fetching group history:', error);
    throw error;
  }
};

// Get recent activity across all user's groups
export const getRecentActivity = async (groups, limit = 10) => {
  try {
    const allActivity = [];
    
    // Fetch history for each group
    for (const group of groups) {
      try {
        const groupHistory = await getGroupHistory(group.id);
        if (groupHistory.items && groupHistory.items.length > 0) {
          // Add group info to each activity item
          const itemsWithGroup = groupHistory.items.map(item => ({
            ...item,
            groupName: group.name,
            groupId: group.id
          }));
          allActivity.push(...itemsWithGroup);
        }
      } catch (error) {
        console.warn(`Failed to load history for group ${group.id}:`, error);
        // Continue with other groups even if one fails
      }
    }
    
    // Sort all activity by date (most recent first)
    const sortedActivity = allActivity.sort((a, b) => {
      if (!a.date && !b.date) return b.id - a.id;
      if (!a.date) return 1;
      if (!b.date) return -1;
      return new Date(b.date) - new Date(a.date);
    });
    
    // Return limited number of recent items
    return sortedActivity.slice(0, limit);
  } catch (error) {
    console.error('Error fetching recent activity:', error);
    throw error;
  }
};