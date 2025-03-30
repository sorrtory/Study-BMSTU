import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class mainPanel {
    public static void main(String[] args) {
        JFrame frame = new JFrame("SmartHouse");

        frame.setContentPane(new mainPanel().mainPanel);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
//        frame.setLocationRelativeTo(null);
        frame.setLocation(1000, 300);
        frame.pack();
        frame.setVisible(true);
    }

    private JPanel mainPanel;
    private JTextField floorTextField;
    private JPanel floorPanel;
    private JLabel floorNow;
    private JButton floorSetButton;
    private JPanel ctrPanel;
    private JPanel drawPanel;
    private JPanel windowPanel;
    private JRadioButton heatingButton;
    private House house;
    private JLabel windowsNow;
    private JButton windowsSetButton;
    private JTextField windowsTextField;

    private int floors = 5;
    private int windows = 3;
    public mainPanel(){
        house.setFloors(floors);
        house.setWindows(windows);

        floorNow.setText("Текущее количество: " + floors);
        windowsNow.setText("Текущее количество: " + windows);

        heatingButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                house.changePipe();
            }
        });
        floorSetButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                floors = Integer.parseInt(floorTextField.getText());
                house.setFloors(floors);
                floorNow.setText("Текущее количество: " + floors);
            }
        });


        windowsSetButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                windows = Integer.parseInt(windowsTextField.getText());
                house.setWindows(windows);
                windowsNow.setText("Текущее количество: " + windows);

            }
        });
    }

}
