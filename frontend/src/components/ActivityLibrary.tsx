// frontend/src/components/ActivityLibrary.tsx
import React from 'react';
import { useDrag } from 'react-dnd';
import { Activity } from '../types';

interface ActivityLibraryProps {
  activities: Activity[];
}

interface ActivityCardProps {
  activity: Activity;
}

const ActivityCard: React.FC<ActivityCardProps> = ({ activity }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'activity',
    item: { ...activity },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
    end: (item, monitor) => {
      const dropResult = monitor.getDropResult();
      if (item && dropResult) {
        console.log(`Dropped ${item.name}`, dropResult);
      }
    },
  }), [activity]);

  return (
    <div
      ref={drag as unknown as React.Ref<HTMLDivElement>}  // Type assertion to fix TS error
      className="activity-card"
      style={{
        opacity: isDragging ? 0.5 : 1,
        backgroundColor: activity.color || '#4CAF50',
        cursor: 'move',
        padding: '10px',
        margin: '5px',
        borderRadius: '5px',
        border: '1px solid #ccc',
        color: 'white',
        fontWeight: 'bold',
      }}
      onClick={() => console.log('Activity clicked:', activity)}
    >
      <h4 style={{ margin: '0 0 5px 0', fontSize: '14px' }}>{activity.name}</h4>
      <p style={{ margin: 0, fontSize: '12px', opacity: 0.9 }}>{activity.duration} min</p>
    </div>
  );
};

const ActivityLibrary: React.FC<ActivityLibraryProps> = ({ activities }) => {
  console.log('ActivityLibrary received activities:', activities);

  return (
    <div className="activity-library">
      <h2>Activity Library ({activities.length})</h2>
      <div className="activity-list">
        {activities.map((activity) => (
          <ActivityCard key={activity.id} activity={activity} />
        ))}
      </div>
    </div>
  );
};

export default ActivityLibrary;